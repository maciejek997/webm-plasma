# webm-plasma

Zależności skryptu:
- Python
- KDialog
- FFmpeg
- libvpx-vp9

Założenia skryptu:

1. Prosty sposób by przekonwertować film do rozmiaru dopuszczalnego przez darmowy plan Discorda (10 MB)

2. Skrypt powinien być dostępny z poziomu menu kontekstowego Plasmy

3. Obliczanie rozmiaru pliku, czy też jego bitrate'u powinno polegać na prostym wzorze:

(docelowy_rozmiar_pliku * megabit_w_kilobitach * przestrzeń_na_audio_i_ewentualny_błąd_pomiaru) / długość filmu * 8

Docelowy rozmiar pliku = 10 MB, co wynika z ograniczeń darmowego planu platformy Discord

Megabit = 1024 Kb; enkoder (w tym przypadku FFmpeg/libvpx-vp9) łatwiej sobie poradzi z kilobitami

Przestrzeń na ewentualny błąd pomiaru = 0.99

^ Użytkownik powinien mieć wybór co do tego czy chce żeby audio było zawarte w przekonwertowanym przez ffmpeg filmie czy też nie.

Jeżeli nie wyrazi takiego zainteresowania zostajemy przy wartości 0.99, gdy jednak użytkownik zechce by audio zostało dodane do filmu wartość powinna się zmienić na 0.975, by zapewnić odpowiednią ilość miejsca dla strumienia audio.

Wykorzystany zostanie kodek audio Opus, ze względu na swoją dużą wydajność, nawet w trudnych warunkach (niski bitrate).

Strumień audio śmiało można zostawić w okolicach 96kb/s, Opus świetnie sobie poradzi w takich warunkach.

Powinen również zostać dodany warunek w którym jeżeli ffprobe wykaże że kodek Opus został wcześniej użyty w pliku źródłowym to FFmpeg będzie miał wskazane by ten strumień audio przekopiować (-c:a copy). Jednak powinny być unikane sytuacje w których bitrate strumienia audio z pliku źródłowego wynosi ~320kb/s, jest to zwyczajnie za dużo dla klipów z gier czy nawet prostych filmów. 

(^ Tutaj trzeba będzie przemyśleć jak to rozwiązać)

Na samym końcu trzeba przemnożyć wszystko przez 8, by uzyskać kilobity zamiast kilobajtów. 

Przykład:

(10 * 1024 * 0.99) / 20 * 8 = ~4055kb/s

Finalnie powinien wyjść film który jest bardzo bliski przekroczenia bariery 10 MB.