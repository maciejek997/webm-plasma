# Overview

Zależności skryptu:
- Python
- KDialog
- FFmpeg
- libvpx-vp9

# Założenia skryptu:

1. Prosty sposób by przekonwertować film do rozmiaru dopuszczalnego przez darmowy plan Discorda (10 MB)

2. Skrypt powinien być dostępny z poziomu menu kontekstowego Plasmy

3. Obliczanie rozmiaru pliku, czy też jego bitrate'u powinno polegać na prostym wzorze:

(docelowy_rozmiar_pliku * megabit_w_kilobitach * przestrzeń_na_audio_i_ewentualny_błąd_pomiaru) / długość filmu * 8

Docelowy rozmiar pliku = 10 MB, co wynika z ograniczeń darmowego planu platformy Discord

Megabit = 1024 Kb; enkoder (w tym przypadku FFmpeg/libvpx-vp9) łatwiej sobie poradzi z kilobitami

Przestrzeń na ewentualny błąd pomiaru = 0.99

^ Użytkownik powinien mieć wybór co do tego czy chce żeby audio było zawarte w przekonwertowanym przez FFmpeg filmie czy też nie.

Jeżeli nie wyrazi takiego zainteresowania zostajemy przy wartości 0.99, gdy jednak użytkownik zechce by audio zostało dodane do filmu wartość powinna się zmienić na 0.975, by zapewnić odpowiednią ilość miejsca dla strumienia audio.

Wykorzystany zostanie kodek audio Opus, ze względu na swoją dużą wydajność, nawet w trudnych warunkach (niski bitrate).

Strumień audio śmiało można zostawić w okolicach 96kb/s, Opus świetnie sobie poradzi w takich warunkach.

Powinen również zostać dodany warunek w którym jeżeli ffprobe wykaże że kodek Opus został wcześniej użyty w pliku źródłowym to FFmpeg będzie miał wskazane by ten strumień audio przekopiować (-c:a copy). Jednak powinny być unikane sytuacje w których bitrate strumienia audio z pliku źródłowego wynosi ~320kb/s, jest to zwyczajnie za dużo dla klipów z gier czy nawet prostych filmów. 

(^ Tutaj trzeba będzie przemyśleć jak to rozwiązać)

Na samym końcu trzeba przemnożyć wszystko przez 8, by uzyskać kilobity zamiast kilobajtów. 

Przykład:

(10 * 1024 * 0.99) / 20 * 8 = ~4055kb/s

Finalnie powinien wyjść film który jest bardzo bliski przekroczenia bariery 10 MB.

# Założenia samego FFmpeg

libvpx-vp9 preferuje enkodowanie dwuprzebiegowe, powinny zostać wykorzystane `-pass 1` i `-pass 2`

### Pierwszy przebieg:

`ffmpeg`

`-hwaccel vaapi -hwaccel_output_format vaapi`: umożliwia wykorzystanie akceleracji sprzętowej do dekodowania pliku źródłowego w celu odciążenia procesora, jeżeli rzecz jasna kodek wideo wykorzystany w pliku źródłowym jest wspierany przez kartę graficzną użytkownika

`-i plik_zrodlowy`: plik wejścia

`-c:v libvpx-vp9`: sprecyzowanie enkodera kodeku wideo, w tym przypadku VP9

`-pass 1`: wskazuje FFmpegowi oraz libvpx-vp9 że mają wykonać pierwszy przebieg enkodowania, podczas którego enkoder tworzy "mapę" bitrate'u

`-b:v (wyliczony_ze_wzoru_bitrate)k`: średni bitrate, który będzie wykorzystany przez enkoder

`-row-mt 1`: umożliwia wykorzystanie całego procesora do procesu enkodowania (w przypadku niższych rozdzielczości enkoder nie ma tyle kolumn i rzędów by zutylizować cały procesor)

`-cpu-used 0 -deadline best`: wskazuje enkoderowi, że powinien enkodować w sposób najbardziej wydajny, w przypadku pierwszego przebiegu można sobie na to pozwolić, bo jest on zwyczajnie szybki

`-g (klatki_na_sekunde * 5)`: wskazuje enkoderowi, by ten tworzył klatki kluczowe (klatki na podstawie których enkoder bazuje podczas procesu enkodowania obrazu) w odstępach pięciu sekund

`-enable-tpl 1`: umożliwia enkoderowi wykorzystanie modelu warstwy czasowej, który pomaga w uzyskaniu dodatkowej wydajności enkodowania

`-auto-alt-ref 1`: umożliwia enkoderowi wykorzystanie alternatywnych klatek referencyjnych, które są dla końcowego użytkownika niewidoczne, a pomagają jeszcze bardziej w wydajności enkodowania

`-arnr-maxframes 7`: maksymalna ilość alternatywnych klatek referencyjnych które enkoder wykorzysta podczas procesu enkodowania

`-arnr-strength 4`: "siła" z jaką enkoder będzie odszumiał alternatywne klatki referencyjne

`-lag-in-frames 25`: ilość klatek jaką enkoder może "zobaczyć" w przód, by pomóc sobie z dodatkowym uzyskaniem lepszej wydajności enkodowania

`-an`: usunięcie strumienia audio

`-sn`: usunięcie metadanych o napisach

`-f null -`: wysłanie wychodzącego strumienia wideo, który i tak byłby pusty do `/dev/null`

### Drugi przebieg

`ffmpeg -hwaccel vaapi -hwaccel_output_format vaapi -i plik_zrodlowy -c:v libvpx-vp9 -pass 1 -b:v (wyliczony_ze_wzoru_bitrate)k -row-mt 1 -cpu-used 3 -deadline good -g (klatki_na_sekunde * 5) -enable-tpl 1 -auto-alt-ref 1 -arnr-maxframes 7 -arnr-strength 4 -lag-in-frames 25 (-c:a copy/-c:a libopus -b:a 96k -vbr on/-an)[w zależności od tego co wybierze skrypt razem z użytkownikiem] -sn -f webm plik_zrodlowy.webm`

#### Co zmieniono względem pierwszego przebiegu?

`-c:a copy`: w przypadku kiedy `ffprobe` wykaże że w pliku źródłowym wykorzystano już kodek Opus/Vorbis

`-c:a libopus -b:a 96k`: w przypadku kiedy w pliku źródłowym wykorzystany został kodek audio AAC, bądź jakikolwiek inny niż Opus/Vorbis

`-an`: w przypadku kiedy użytkownik nie chce strumienia audio w swoim filmie

`-cpu-used 3` - wskazuje enkoderowi by nadal wydajnie enkodował wychodzące wideo, lecz po prostu zrobił to szybciej (-cpu-used >3 wyłącza RDO: Rate-distortion Optimization, wychodzący film powinien jednak wyglądać dobrze)

`-deadline good`:  w przypadku drugiego przebiegu enkodowania `-deadline best` jest zbędny, zajmuje zbyt dużo czasu i nie oferuje znacznie zwiększonej jakości (o ile w ogóle) i ogranicza się do wykorzystywania czterech wątków procesora