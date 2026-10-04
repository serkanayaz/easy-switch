# easy-switch

[English](README.md) | **Türkçe**

Logitech mouse'u (veya klavyeyi) tek bir butonla başka bir Easy-Switch kanalına geçiren küçük bir Windows aracı.

Logitech MX serisi cihazlar üç bilgisayara/cihaza kadar eşleşebilir ve aralarında cihazın altındaki Easy-Switch butonuyla geçiş yapılır. Logi Options+ bu geçişi bir butona doğrudan atamaya izin vermez; yalnızca Actions Ring üzerinden, iki adımda yapılabilir. **easy-switch** bu boşluğu kapatır: Options+'ta herhangi bir butona bu programı atadığınızda, tek basışta cihaz diğer kanala geçer.

Program iki biçimde kullanılabilir: Python yüklü bilgisayarlarda doğrudan Python koduyla (`.exe` gerekmez) ya da Python gerektirmeyen hazır bir `.exe` ile. Ayrıntılar [Kurulum](#kurulum) bölümünde.

## Nasıl çalışır

Program, cihazın kendi Easy-Switch butonunun gönderdiği komutun aynısını gönderir: HID++ 2.0 protokolündeki `CHANGE_HOST` (`0x1814`) özelliği.

1. Bilgisayardaki HID cihazları taranır:

   | Bağlantı | HID++ kanalı (usage page / usage) | Cihaz indeksi |
   | --- | --- | --- |
   | Logitech alıcısı (Bolt, Unifying, Lightspeed...) | `0xFF00` / `0x0002` | `1`..`6` |
   | Doğrudan Bluetooth | `0xFF43` / `0x0202` | `0xFF` |

2. Her cihazın adı `DEVICE_NAME` (`0x0005`) özelliğiyle okunur, istenen cihaz adıyla bulunur. Aynı alıcıda Easy-Switch destekleyen başka bir cihaz (örneğin klavye) olabileceği için seçim ada göre yapılır.
3. `CHANGE_HOST.getHostInfo` ile kanal sayısı ve şu anki kanal okunur.
4. `CHANGE_HOST.setCurrentHost` ile hedef kanala geçilir. Cihaz bağlantıyı hemen bıraktığı için bu komutun cevabı beklenmez.

Bilgisayara özel bir ayar yoktur; aynı program her bilgisayarda çalışır.

## Kanal seçimi

Hedef kanal, sırasıyla şuradan okunur:

1. **Komut satırı argümanı:** `easy-switch.exe 3` ya da `python easy_switch.py 3`
2. **Programın dosya adı:** `easy-switch-3.exe` ya da `easy-switch-3.pyw` → 3. kanal
3. Hiçbiri yoksa **sıradaki kanal** (1 → 2 → 3 → 1)

Logi Options+ programa argüman geçiremediği için 2. yol vardır: her kanal için aynı programın, adının sonunda kanal numarası olan bir kopyası kullanılır.

| Python ile | `.exe` ile | Davranış |
| --- | --- | --- |
| `easy-switch.pyw` | `easy-switch.exe` | Sıradaki kanala geçer |
| `easy-switch-1.pyw` | `easy-switch-1.exe` | 1. kanala geçer |
| `easy-switch-2.pyw` | `easy-switch-2.exe` | 2. kanala geçer |
| `easy-switch-3.pyw` | `easy-switch-3.exe` | 3. kanala geçer |

Cihaz zaten hedef kanaldaysa program hiçbir şey yapmaz.

## Kurulum

İki yol var; ikisi de aynı işi yapar:

| | A. Python ile (`.pyw`) | B. Hazır program ile (`.exe`) |
| --- | --- | --- |
| Ne zaman? | `.exe` çalıştırmanın yasak olduğu ya da `.exe`'nin antivirüse takıldığı bilgisayarlar | Python kurmak istemeyenler |
| Gereken | Python (ek paket yok) | Hiçbir şey |
| Options+ eylemi | **Open file** | **Open application** |

> [!NOTE]
> Program yalnızca kurulu olduğu bilgisayarda çalışır. Cihaz başka bir bilgisayara geçtiğinde geri dönmek için ya o bilgisayara da programı kurup butonu atayın ya da cihazın kendi Easy-Switch butonunu kullanın.

### A. Python ile çalıştırma (`.exe` gerekmez)

Python'ı daha önce hiç kurmadıysanız baştan sona şu adımları izleyin.

#### 1. Python'ı kurun

1. <https://www.python.org/downloads/windows/> adresini açın. **Stable Releases** başlığı altında en üstteki sürümlerden birinin altındaki **Download Windows installer (64-bit)** bağlantısına tıklayın. İnen dosyanın adı `python-3.x.x-amd64.exe` gibi olmalıdır.
2. İnen kurulum dosyasını çalıştırın.
3. İlk ekranın altındaki iki kutuyu işaretleyin:
   - **Use admin privileges when installing py.exe**
   - **Add python.exe to PATH**
4. **Install Now**'a basın ve kurulumun bitmesini bekleyin.

> [!IMPORTANT]
> Python kurulum dosyasının kendisi de bir `.exe`'dir. `.exe` çalıştırmanın yasak olduğu bilgisayarlarda Python'ı kurması için bilgi işlem biriminden destek isteyin; çoğu kurumda Python onaylı yazılımlar arasındadır. Python bir kez kurulduktan sonra bu program için başka hiçbir şey kurmanız gerekmez.

**Kontrol:** Başlat menüsüne `cmd` yazıp **Komut İstemi**'ni açın ve şunu yazın:

```bat
python --version
```

`Python 3.12.5` gibi bir sürüm numarası görmelisiniz. Program Python 3.10 ve üstüyle çalışır.

#### 2. Program dosyalarını indirin

1. Bu GitHub sayfasında yeşil **Code** butonuna, ardından **Download ZIP**'e basın.
2. İnen ZIP dosyasına sağ tıklayıp **Tümünü ayıkla** deyin.
3. Çıkan klasörü kalıcı bir yere taşıyın, örneğin `C:\Tools\easy-switch`. Options+ dosyayı bu adresten çağıracağı için klasörün yeri sonradan değişmemeli.

Klasörde şu dosyaların olması yeterlidir; `dist/` klasörüne bu yol için gerek yoktur:

| Dosya | Görevi |
| --- | --- |
| `easy_switch.py` | Programın kendisi; her zaman gerekli |
| `easy-switch.pyw` | Sıradaki kanala geçer |
| `easy-switch-1.pyw` | 1. kanala geçer |
| `easy-switch-2.pyw` | 2. kanala geçer |
| `easy-switch-3.pyw` | 3. kanala geçer |

`.pyw` dosyaları, programı siyah konsol penceresi açmadan çalıştıran küçük başlatıcılardır. Hangi kanala geçileceğini dosyanın adı belirler. `easy_switch.py` ile aynı klasörde durmaları gerekir.

#### 3. Programı deneyin

Mouse'u hareket ettirip uyandırın. Komut İstemi'nde klasöre geçin ve programı deneme modunda çalıştırın. Bu mod kanal değiştirmez, yalnızca ne yapacağını söyler:

```bat
cd C:\Tools\easy-switch
python easy_switch.py --dry-run
```

Şuna benzer bir satır görmelisiniz:

```text
2026-10-05 01:49:49 [dry-run] 2. kanaldan 3. kanala geçilecekti
```

Mouse'unuz MX Master 4 değilse cihazın adını verin: `python easy_switch.py --device "MX Anywhere 3" --dry-run`. Ad bulunamazsa hata mesajında bilgisayarda görülen Logitech cihazlarının adları listelenir.

#### 4. Logi Options+'a bağlayın

1. Logi Options+'ı açın ve mouse'unuza tıklayın.
2. Mouse resminde geçiş için kullanmak istediğiniz butona tıklayın (örneğin yan taraftaki **Forward** butonu). O butonun eski görevi kaybolacaktır.
3. Sağda açılan eylem listesinde **Open file**'ı seçin.
4. **BROWSE FILE**'a basın ve istediğiniz `.pyw` dosyasını seçin, örneğin `C:\Tools\easy-switch\easy-switch-3.pyw`.
5. Butona basın. Mouse yaklaşık yarım saniye içinde diğer cihaza geçer.

> [!TIP]
> Butona basınca hiçbir şey olmuyorsa klasördeki `easy-switch.log` dosyasına bakın. Dosya hiç oluşmadıysa Windows `.pyw` dosyalarını Python'la açmıyor demektir; `.pyw` dosyasına sağ tıklayıp **Birlikte aç** → **Python** → **Her zaman bu uygulamayı kullan** seçin ve tekrar deneyin.

### B. Hazır program ile çalıştırma (`.exe`)

#### Hazır `.exe`'leri kullanmak

1. `.exe` dosyalarını [son sürümün sayfasından](https://github.com/serkanayaz/easy-switch/releases/latest) indirin ve kalıcı bir klasöre koyun, örneğin `C:\Tools\easy-switch`.

   | Dosya | Davranış |
   | --- | --- |
   | `easy-switch.exe` | Sıradaki kanala geçer |
   | `easy-switch-1.exe` | 1. kanala geçer |
   | `easy-switch-2.exe` | 2. kanala geçer |
   | `easy-switch-3.exe` | 3. kanala geçer |

2. Logi Options+ → mouse'unuz → geçiş için kullanacağınız buton → eylem listesinden **Open application** → **BROWSE APPLICATION** → istediğiniz `.exe`.
3. Butona basın.

İlk çalıştırmada Windows SmartScreen "Windows bilgisayarınızı korudu" uyarısı verebilir. Program imzasız olduğu için bu normaldir; **Ek bilgi** → **Yine de çalıştır** ile devam edebilirsiniz.

#### `.exe`'leri kendiniz derlemek

Hazır dosyalara güvenmek yerine `.exe`'leri kaynak koddan kendiniz üretebilirsiniz. Bunun için A yolundaki 1. ve 2. adımlarla Python'ı kurup dosyaları indirmeniz gerekir. Ardından Komut İstemi'nde:

```bat
cd C:\Tools\easy-switch
pip install pyinstaller
pyinstaller --onefile --windowed --name easy-switch --exclude-module hid easy_switch.py

cd dist
copy easy-switch.exe easy-switch-1.exe
copy easy-switch.exe easy-switch-2.exe
copy easy-switch.exe easy-switch-3.exe
```

- `--onefile`: her şeyi tek bir `.exe` dosyasına koyar.
- `--windowed`: konsol penceresinin açılmasını engeller.
- `--exclude-module hid`: Windows'ta gerekmeyen `hidapi` paketini dışarıda bırakır.

`.exe`'ler `dist` klasöründe oluşur. Dört dosya aslında aynıdır, yalnızca adları farklıdır; hangi kanala geçileceğini ad belirler. Deneme için `dist\easy-switch.exe --dry-run` çalıştırıp sonucu `dist\easy-switch.log` dosyasında görebilirsiniz. Options+'a bağlamak için yukarıdaki adımları izleyin.

### Güvenlik

Program klavye ya da mouse girdisi **okumaz**. Yalnızca Logitech'in HID++ kanalını açar, cihaza kendi komutlarını yazar ve yalnızca bu komutların cevaplarını okur. Klavye ve mouse kanalları Windows tarafından işletim sistemine ayrılmıştır; program bunlara erişmez. Windows'ta HID erişimi `ctypes` ile Windows'un kendi `hid.dll` / `setupapi.dll` dosyaları üzerinden yapılır; dışarıdan paket gelmez. Kodun tamamı tek bir okunabilir dosyadadır: `easy_switch.py`.

### macOS ve Linux

`pip install hidapi` ile `hidapi` paketini kurup `python3 easy_switch.py --dry-run` ile deneyin. Bu platformlar denenmemiştir.

## Komut satırı

```text
easy-switch.exe [KANAL] [--device AD] [--dry-run]
python easy_switch.py [KANAL] [--device AD] [--dry-run]
```

İki biçim aynı seçenekleri alır; aşağıdaki örneklerde `easy-switch.exe` yerine `python easy_switch.py` yazılabilir.

| Seçenek | Açıklama |
| --- | --- |
| `KANAL` | Geçilecek kanal (`1`, `2`, `3`). Verilmezse dosya adına bakılır, orada da yoksa sıradaki kanal seçilir. |
| `--device AD` | Hedef cihazın adı; ad içinde aranır, büyük/küçük harf duyarsızdır. Varsayılan: `MX Master 4`. |
| `--dry-run` | Kanal değiştirmez, yapılacak işi log dosyasına yazar. |

Örnekler:

```bash
easy-switch.exe 2
easy-switch.exe --device "MX Keys" 3
easy-switch.exe --dry-run
```

## Log ve hatalar

Her çalışma, programın bulunduğu klasördeki `easy-switch.log` dosyasına bir satır yazar. Dosya 256 KB'ı geçince `easy-switch.log.1` olarak saklanır.

Konsolsuz çalışırken bir hata olursa ayrıca ekranda bir uyarı penceresi açılır. Sık görülen hatalar:

| Hata | Çözüm |
| --- | --- |
| `... bulunamadı; uyuyor ya da bu bilgisayara bağlı değil olabilir` | Cihazı hareket ettirip uyandırın. Mesajın sonunda o bilgisayarda görülen Logitech cihazlarının adları listelenir; `--device` ile bunlardan biri seçilebilir. |
| `kanal N geçersiz; cihazda M kanal var` | Dosya adındaki veya argümandaki kanal numarası cihazın kanal sayısından büyük. |

Cihaz bulunamadığında program takılı tüm alıcıları taradığı için hata birkaç saniye sonra gelir; normal geçiş anında olur.

## Gereksinimler ve sınırlar

- Windows 10/11; `.exe` için hiçbir şey, `.pyw` için yalnızca Python gerekir. Kaynak kod macOS ve Linux'ta da `hidapi` ile çalışabilir, ancak bu platformlarda denenmemiştir.
- Cihazın HID++ 2.0 `CHANGE_HOST` özelliğini desteklemesi gerekir (Easy-Switch butonu olan güncel Logitech cihazları).
- Logi Options+ açıkken de çalışır; ona dokunmaz.
- Test edilen: MX Master 4, Logi Bolt alıcısı, Windows 11.

## Dosyalar

| Dosya | İçerik |
| --- | --- |
| `easy_switch.py` | Programın tamamı |
| `easy-switch*.pyw` | Konsolsuz Python başlatıcıları |
| `dist/README.txt` | `.exe`'lerle birlikte dağıtılan kısa kullanıcı notu |

Derlenmiş `.exe` dosyaları depoda tutulmaz; [Releases](https://github.com/serkanayaz/easy-switch/releases) sayfasında yayınlanır.

## Lisans

[MIT](LICENSE)
