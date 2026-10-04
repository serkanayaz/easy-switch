Easy-Switch — mouse'u bir butonla başka bir Easy-Switch kanalına geçirir
=======================================================================

Bu klasörü herhangi bir Windows bilgisayara kopyalamak yeterli; Python gerekmez.

  easy-switch.exe     sıradaki kanala geçer (1 -> 2 -> 3 -> 1)
  easy-switch-1.exe   1. kanala geçer
  easy-switch-2.exe   2. kanala geçer
  easy-switch-3.exe   3. kanala geçer

Kanalı dosya adının sonundaki sayı belirler; dosyalar aslında aynıdır.

Logi Options+ ayarı:
  MX Master 4 -> istenen buton -> "Open application" -> BROWSE APPLICATION
  -> bu klasördeki istenen .exe

Bir bilgisayardan kendi kanalına geçmek bir şey yapmaz; o bilgisayarda
easy-switch.exe (sıradaki) ya da diğer kanalların dosyaları kullanılır.

Komut satırı:
  easy-switch.exe 3                     3. kanala geç
  easy-switch.exe --device "MX Keys"    başka bir Logitech cihazını geçir
  easy-switch.exe --dry-run             geçmeden ne yapılacağını log'a yaz

Hatalar ekranda uyarı olarak çıkar ve easy-switch.log dosyasına yazılır.

.exe çalıştırılamıyorsa:
  Aynı program Python ile de çalışır, ek paket gerekmez. Projenin kök
  klasöründeki easy_switch.py ile istenen .pyw dosyasını (easy-switch.pyw,
  easy-switch-1.pyw ...) aynı klasöre kopyalayın; Options+'ta "Open file"
  eylemiyle .pyw dosyasını seçin.
