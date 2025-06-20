# OzHash Şifreleme Algoritması

OzHash, tarafımdan Python programlama dilini ve kriptografik prensipleri öğrenmek amacıyla geliştirilmiş özgün bir hash (karma) algoritmasıdır.

##  Genel Bakış ve Hedefler

OzHash, bir parola veya herhangi bir metin girdisini, yapılandırılabilir parametrelere dayalı olarak sabit uzunlukta, deterministik bir hash değerine dönüştürür. Algoritmanın temel hedefleri şunlardır:

*   **Deterministik Olma:** Aynı girdi, tuz (salt) ve tohum (seed) ile her zaman aynı çıktıyı üretir. Bu, parola doğrulaması için zorunludur.
*   **Yapılandırılabilirlik:** Matris boyutu, iterasyon sayısı, bellek kullanımı gibi parametreler ayarlanabilir. Bu sayede güvenlik seviyesi, donanıma göre ölçeklendirilebilir.
*   **Bellek Yoğunluk (Memory-Hardness):** Algoritma, işlemci gücünün yanı sıra önemli miktarda bellek kullanımını da gerektirir. Bu, kaba kuvvet (brute-force) ve paralel işlem saldırılarına karşı direnci artırır.
*   **Argon2 Benzeri Çıktı Formatı:** Üretilen hash, doğrulama için gerekli olan tüm parametreleri (tuz, tohum, vb.) içeren, kendi kendini tanımlayan bir formatta sunulur.

## Proje Dosya Yapısı

Proje, görevlerine göre modüler dosyalara ayrılmıştır:

*   `main.py`: `OzHash` ana sınıfını içerir. Şifreleme (`encrypt`) ve doğrulama (`verify`) süreçlerini yönetir ve diğer modülleri orkestra eder.
*   `key_schedule.py`: Verilen anahtar (parola) ve tuzdan yola çıkarak, algoritmanın başlangıcında kullanılacak olan anahtar matrislerini üretir.
*   `matrix_operations.py`: Algoritmanın kalbi olan, matrisler üzerinde veriye bağımlı ve bağımsız karıştırma (mixing) operasyonlarını gerçekleştirir.
*   `memory_manager.py`: Algoritma boyunca kullanılacak olan deterministik bellek bloklarını ve havuzlarını yönetir.
*   `password_verify.py`: Komut satırından parola doğrulama işlemini gerçekleştirmek için bir yardımcı araçtır.
*   `errors.py`: Projeye özgü hata sınıflarını (`ConfigurationError`, `VerificationError` vb.) tanımlar.

## Algoritmanın Matematiksel Temelleri

OzHash, temel olarak matris operasyonları, modüler aritmetik ve doğrusal olmayan (non-linear) fonksiyonlar üzerine kuruludur. Algoritmanın adımları matematiksel olarak şu şekilde ifade edilebilir:

### 1. Başlatma ve Anahtar Türetme

Algoritma, bir parola `P`, rastgele bir tuz `S` ve deterministik operasyonlar için bir tohum `s` (seed) ile başlar.

*   **İlk Karma (Initial Hash):** Parola ve tuz birleştirilerek kriptografik bir karma fonksiyonundan (BLAKE2b) geçirilir ve bir başlangıç değeri `H₀` elde edilir.
    ```
    H₀ = BLAKE2b(P || S)
    ```
    Burada `||` birleştirme (concatenation) anlamına gelir.

*   **Anahtar Matrislerinin Üretimi:** `KeyScheduler`, `H₀`'ı kullanarak bir dizi başlangıç matrisi `Mₖ` oluşturur. Her matris, farklı bir modüler taban `Bₖ` kullanılarak üretilir. Bir matrisin `(i, j)` konumundaki elemanı şu formülle hesaplanır:
    ```
    Mₖ[i, j] = (H₀[index] + i * j + Mem[i, j]) mod Bₖ
    ```
    Burada `Mem[i, j]`, `memory_manager` tarafından tohum (`s`) kullanılarak deterministik olarak üretilen bir bellek değeridir.

### 2. Doğrusal Olmayan Dönüşümler (Non-Linear Transformations)

Başlangıç matrisleri, her bir elemanına aşağıdaki gibi bir dönüşüm fonksiyonu `f(v)` uygulanarak daha karmaşık hale getirilir. Bu adım, sistemin doğrusallığını kırarak analitik çözümü zorlaştırır.
```
f(v) = (sin(v) + cos(v) + exp(v mod C)) mod Bₖ
```
Burada `C`, `exp` fonksiyonunun argümanını sınırlamak için kullanılan bir sabittir. Trigonometrik ve üstel fonksiyonların kullanılması, matris elemanları arasında karmaşık, doğrusal olmayan ilişkiler yaratır.

### 3. İteratif Karıştırma ve Bellek Erişimi (Iterative Mixing)

Bu, algoritmanın en kritik adımıdır. `MatrixHandler`, matrisleri `N` iterasyon boyunca günceller. Her iterasyonda, veriye bağımlı veya veriden bağımsız bellek erişim desenleri kullanılır.

*   **Veriden Bağımsız Erişim:** Matrisin bir elemanı, konumu `(i, j)`'ye göre belirlenen bir bellek adresi kullanılarak güncellenir. Bu, deterministik ve öngörülebilir bir karıştırma sağlar.
    ```
    M_new[i, j] = (M_old[i, j] + Mem[i, j]) mod Bₖ
    ```

*   **Veriye Bağımlı Erişim:** Matrisin bir elemanı, *kendi değeri* tarafından belirlenen bir bellek adresi kullanılarak güncellenir. Bu, algoritmanın "bellek-zor" (memory-hard) olmasını sağlayan temel mekanizmadır. Erişim deseni, matrisin mevcut durumuna bağlı olduğu için, işlemci cache'lerinden verimli bir şekilde yararlanmayı zorlaştırır ve paralel saldırıları yavaşlatır.
    ```
    M_new[i, j] = (M_old[i, j] + Mem[i, M_old[i, j] mod S_mem]) mod Bₖ
    ```
    Burada `S_mem` bellek havuzunun boyutudur.

Bu iki işlem, iterasyonlar boyunca dönüşümlü olarak uygulanarak hem karmaşıklık hem de güvenli bellek erişimi sağlanır.

### 4. Sonuç Hash'in Üretilmesi

`N` iterasyon tamamlandıktan sonra, son halini alan matrisler düzleştirilir (flattened), yani tek boyutlu bir diziye dönüştürülür. Bu diziler, onaltılık (hex) formata çevrilir ve birleştirilerek ham hash (`RawHash`) oluşturulur.
```
RawHash = Flatten(M_final,1) || Flatten(M_final,2) || ...
```
Bu `RawHash`, tuz, tohum ve kullanılan parametrelerle birlikte Base64 formatında kodlanarak nihai çıktı dizesi oluşturulur:
`$ozhash$v=1$params$seed$salt$hash`

## Kullanım Örneği

Aşağıda, `OzHash` sınıfının temel kullanımı gösterilmiştir.

```python
from main import OzHash
import os

# Algoritma için yapılandırma
config = {
    "matrix_size": 8,
    "memory_blocks": 4,
    "iterations": 12,
    "mod_bases": [353, 509, 613],
    "memory_size": 2048,
    "process_mode": "adaptive"
}

# OzHash örneği oluştur
ozhash = OzHash(config)

# Parola, tuz ve tohum
password = "securepassword"
salt = ozhash.generate_salt()
seed = int.from_bytes(os.urandom(4), 'big')

# Parolayı hash'le
encoded_hash = ozhash.encrypt(password, salt, seed)
print("Üretilen Hash:", encoded_hash)

# Doğrulama
is_verified = ozhash.verify(password, encoded_hash)
print("Doğrulama Sonucu:", is_verified)
``` 
