# Центральна база даних Dozorro
-------------------------------
_Статус документу: чернетка, версія 20 квітня 2017_

## Зміст

1. [Призначення](#_1)
2. [Принципи роботи ЦБД](#_2)
3. [Правила роботи майданчиків](#_3)
4. [Протокол обміну даними](#_4)
5. [Отримання даних](#_5)
6. [Швидка синхронізація](#_6)
7. [Структура даних](#_7)
8. [Моделі даних](#_8)
9. [Cхеми даних](#_9)
10. [Шаблони форм](#_10)
11. [Заповнення author](#_11)
12. [Розрахунок ID та підпису](#_12)
12.1. Розрахунок HASH-ID
12.2. Розрахунок підпису
13. [Відправка даних](#_13)
14. [Корисні посилання](#_14)


## Призначення

Центральна база даних моніторингового порталу **Dozorro** призначена для зберігання і поширення відгуків на тендери в системі публічних закупівель **Prozorro**, а також коментарів до них та іншої пов'язаної інформації.

## Принципи роботи ЦБД

1. Центральна база даних є публічною за принципом "всі бачать все";
2. В базу можна тільки додавати дані, **не можна** редагувати, або видаляти записи;
3. Права додавання даних є тільки у авторизованих майданчиків;
4. Права на читання є у всіх;
5. Будь-хто може перевірити джерело походження даних та їх автентичність.

## Правила роботи майданчиків

1. Майданчик відображає всі наявні відгуки і коментарі до тендера без виключення;
2. Майданчик надає можливість залишати відгуки замовникам та постачальникам;
3. Можливість анонімного коментування доступна **тільки** для перевіриних користувачів;
4. Для відправки даних майданчик реєструє свій публічний ключ в ЦБД;
5. Майданчик підписує всі данні які відправляються в ЦБД.

## Протокол обміну даними

1. Доступ до ЦБД відбувається за протоколом HTTP через REST-подібне API;
2. Дані представлені у форматі JSON в кодуванні UTF-8 без `\u0000` екранування;
3. Дата та час записуються як строки за стандартом ISO 8601;
4. ID запису - це хеш від даних, тому повторне додання однакових даних неможливе;
5. ЦБД містить як відгуки так і технічну інформацію (публічні ключі, відгуки, тощо);

**Тестове середовище** — https://api-sandbox.dozorro.org/

## Отримання даних

1. Отримання списку ID записів
    - першої сторінки: https://api-sandbox.dozorro.org/api/v1/data
    - другої сторінки: https://api-sandbox.dozorro.org/api/v1/data?offset={next_page}
    - останньої сторінки: https://api-sandbox.dozorro.org/api/v1/data?reverse=1
2. Отримання запису по його ID
    - одного: [/api/v1/data/0000e550ab57d14d40791816fc5bc468](https://api-sandbox.dozorro.org/api/v1/data/0000e550ab57d14d40791816fc5bc468)
    - декількох одним запитом: [/api/v1/data/{id-1},{id-2},{id-3}](https://api-sandbox.dozorro.org/api/v1/data/6f65da0f1368de369bf808f962e28294,223efa60c127db93926da8a17d3a0f25,8bd6ad9acd72c60e8e7f40ab1c76509a)
    - при отриманні декількох об'єктів одним запитом помилки ЦБД ігноруються, клієнт має самостійно контролювати кількість отриманих записів та їх ID.
3. Оскільки всі записи в ЦБД незмінні _(англ. immutable)_ та ID запису це хеш від даних — то коднтролю дати змін та повторного скачування не потрібно, достатньо порівняти ID.

## Швидка синхронізація

1. Отримати `offset` з останньої сторінки: [/api/v1/data?reverse=1](https://api-sandbox.dozorro.org/api/v1/data?reverse=1)
2. Продовжити рух паралельно _двома курсорами_ в двох напрямах:
    - "прямому" від останньої сторінки до наступної отримуючи останні оновлення;
    - "звіротньому" від останньої сторінки назад до першої в режимі `reverse`.
3. Дійшовши "зворотнім" курсором до першої сторінки закрити його залишивши для подальшої синхронізації тільки "прямий".

[Скоро] для зменшення кількості запитів переключити "прямий" курсор в режим **WebSocket**.
Повну синхронізацію рекомендується робити раз на добу (краще вночі).

## Структура даних

1. На верхньому рівні будь-який запис містить `id`, `sign`, `envelope`
2. ID та підпис розраховуються від `envelope` серіалізованого в JSON
3. `envelope` містить наступні обов'язкові поля:
    - `date` — дата та час створення в ISO 8601
    - `model` — модель даних (_form_ або _comment_)
    - `schema` — схема даних в payload (_tender101_, _tender102_, ...)
    - `owner` — назва майданчика
    - `payload` — корисний вміст
        - `autor`
        - `formData`
        - `tender`
4. Перелік полів фіксований тільки для `envelope`, все що в `payload` описує конкретна схема.

#### Приклад
```json
{
  "id":               "( 2 x sha256 hash of envelope in hex )",

  "sign":             "( Ed25519 sign of envelope in base64 )",

  "envelope": {
    "date":           "2016-11-01T11:28:57+00:00",
    "model":          "form",
    "schema":         "tender101",
    "owner":          "dozorro.org",

    "payload": {
      "author":       {  },
      "formData":     {  },
      "tender":       "8243e24e516142f8952ff32d3af93880"
    }
  }
}
```

#### Більше прикладів

Правильні та неправильні _(*-bad.json)_ приклади в [dozorro-schemas] в директорії `examples`

##  Моделі даних

Наразі зараз ЦБД допускає три моделі даних:
- `admin` - службова інформація
- `form` - відгуки (заповненні форми tender101 - tender113)
- `comment` - коментарі до форм

## Cхеми даних

1. Всі дані в ЦБД перевіряються на відповідність схемам за допомогою [json-schema]
2. Перелік схем які використовуються в ЦБД доступний в [dozorro-schemas]
3. Схеми також містять опис форм з перекладом інтерфейсу на три мови (укр, рус, eng)

## Шаблони форм

1. Опис форм для збору відгуків міститься прямо в [dozorro-schemas] поле `formData:form`
2. Для рендерінгу форм сайт dozorro використовує модифіковану [jsonform-wiki]
3. Приклад рендерігну HTML form за цими схемами доступний в [Playground]
4. Майданчики можуть використовувати власний спосіб відображення форм за умови збереження переліку полей та запропонованих в схемах формулювань.

**Тестове середовище** — http://jsonform.ed.org.ua/playground/

## Заповнення author

Структура `author` розрізняє наступні випадки

1. По способу авторизації
    1.1 Автор авторизований як замомник або постачальник `scheme: "internal"`
    1.2 Автор авторизований через соціальні мережі `scheme: "external"`

2. За анонімністю допису
    2.1. Залишено відгук з підписом (заповнено name, contactPoint)
    2.2. Залишено анонімний відгук або коментар (name не заповнено)

3. За ролю автора (тільки для dozorro)
    3.1 Поле `procuringEntityRelation` ["commissioner", "supervisor"]

#### author:auth:id

1. Для авторів авторизованих через соціальні мережі `HMAC( user.unique_key )`
2. Для замовників та постачальників (identifier:id = ЄДРПОУ)
2.2. Для відгуків з підписами `HMAC( secret_key, identifier.id )`
2.3. Для анонімних відгуків - `HMAC( secret_key, identifier.id + tender.id )`
3. Рекомендовано використовувати різні ключі HMAC для дописів що містять ім'я та анонімів.

#### Приклад
Автор - замовник або постачальник (присутній код ЄДРПОУ)
```json
{
  "author": {
    "auth": {
      "id": "01db9b12...24a9d3ad = HMAC( identifier.id )",
      "scheme": "internal"
    },
    "address": { },
    "contactPoint": { },
    "identifier": {
      "id": "12345678",
      "scheme": "UA-EDR"
    },
    "name": "PJSC KALYNA"
  }
}
```

Автор - анонім (але був авторизований як замовник або постачальник, присутня scheme)
```json
{
  "author": {
    "auth": {
      "id": "db9b1259...3ad01834 = HMAC( identifier.id + tender.id )",
      "scheme": "internal"
    }
  }
}
```

Детальна схема структури `author` описана в [dozorro-schemas] файл comment/comment.json
Більше прикладів в [dozorro-schemas] в підпапці author

## Розрахунок ID та підпису

1. Мінімальний (пустий) запис даних виглядає як `{"envelope":{}}`
2. Серіалізація в JSON відбувається за правилами:
2.1 кодування UTF-8 та **без** `\u0000` екранування;
2.2 компактно, без пробілів між `"key": "value"` та відступів;
2.3 порядок ключів має бути відсортований в алфавітному порядку.

#### Приклад

**Неправильно (ключі не за алфавітом + зайві пробіли):**
```json
{"envelope": {"c": 1, "b": "тест","a": 5,"owner": "my-name"}}
```
**Неправильно (залишилось екранування unicode):**
```json
{"envelope":{"a":5,"b":"\\u0442\\u0435\\u0441\\u0442"}}
```
**Правильно:**
```json
{"envelope":{"a":5,"b":"тест","c":1,"owner":"dozorro.org"}}
```

### Розрахунок HASH-ID

1. ID даних розраховується як подвійний хеш SHA-256 від даних _envelope_:
    - `SHA256( SHA256( {envelope} ) ).toHex().first(32)`
2. Перша ітерація SHA не кодується в hex (на вхід 2 раунду йдуть бінарні дані)
3. Для ID використовуємо перші 32 символи hex кодування.

#### Приклад

**Перевірте себе**
```json
{"envelope":{},"id":"c74f3008fdd2f7c5ae5446ab2e522629"}
```
**Пояснення**
1. Для розрахунку беруться значення _envelope_ тобто 2 байти `{}`
2. `sha256( sha256('{}').raw() ).hex() = c74f3008 fdd2f7c5 ae5446ab 2e522629 f63346f6 8a4026b4 f72b91b3 93475ff6`
3. Для ID використовуємо перші 32 символи хешу в hex кодуванні.

**За допомогою python**
```python
import json
import hashlib

raw = json.dumps(data,
                 ensure_ascii=False,       # allow unicode chars
                 sort_keys=True,           # sort keys
                 separators=(',', ':'))    # compact, without spaces

h1 = hashlib.sha256(raw).digest()
h2 = hashlib.sha256(h1).hexdigest()

data['id'] = h2[:32]
```

**На PHP**
```php
$sorted_env = recursive_ksort($data['envelope']);  // implement this
$raw = json_encode($sorted_env);
$h1 = hash('sha256', $data, true);
$h2 = hash('sha256', $h1);
$data['id'] = substr($h2, 0, 32);
```

Далі наведено декілька типових помилок:

**Неправильно**
```
sha256( sha256('{}').hex() ).hex() = b8a41204 ... 5a0ff495
```
— зайве hex кодування на першій ітерації

**Неправильно**
```
sha256( sha256('{"envelope":{}}') ).hex() = 2185bc98 ... 274fb452
```
— використані всі дані, а не тільки значення _envelope_

**Неправильно**
```
sha256(sha256('{"c": 1,"a": "\\u0442"}')).hex() = 2185bc98 ... 274fb452
```
— некоректна серіалізація (ключі не за алфавітом, зайві пробіли, unicode екранування)

**Перевірте себе №2**
```json
{"envelope":{"owner":"example-owner"},"id":"f78e26a9166e7812987f9aec721ba2a2"}
```

**Перевірте себе №3**
```json
{"envelope":{"date":"2017-04-20T01:55:21.358240+03:00","owner":"example-owner","payload":"тест"},"id":"061002ffb700a3d7cad59da4457c3af0"}
```
— зверніть увагу на "тест" в utf-8

### Розрахунок підпису

1. Підпис розраховується за алгоритмом [Ed25519](http://ed25519.cr.yp.to)
2. Правила серіалізації JSON такі самі як для розрахунку HASH-ID
3. Результат підпису кодується в `base64` та записується в поле `sign`
4. Для генерації ключів та перевірки себе використовуйте [dozorro-keytool]

**Корисно**

* Перелік сторонніх [бібліотек](https://download.libsodium.org/doc/bindings_for_other_languages/) для різних мов програмування.

#### Приклад

**За допомогою утиліти dozorro-keytool (admin-keytool)**

    $ python3 admin-keytool.py generate
    $ python3 admin-keytool.py export example-owner
    $ python3 admin-keytool.py sign data.json
    $ python3 admin-keytool.py verify data.json
    Load public key data from pubkey.json
    Verify any data json from data.json
    Result OK

    $ cat data.json
    {"envelope":{"owner":"example-owner"},"id":"f78e26a9166e7812987f9aec721ba2a2","sign":"GCI7/vRbT3yUrsp1irQd1JO8Ct1t5LmYECOJ9ohLdpjFAC+U3+57+rqIWSTsF5uxeDZZMIlnsb2fVTwRIYlXCg"}


**За допомогою python**
```python
import json
import ed25519

raw = json.dumps(data,
                 ensure_ascii=False,       # allow unicode chars
                 sort_keys=True,           # sort keys
                 separators=(',', ':'))    # compact, without spaces

sk = ed25519.SigningKey(keydata)

data['sign'] = sk.sign(data_bin, encoding='base64')

```

**На PHP**
```php
$sorted_env = recursive_ksort($data['envelope']);  // implement this
$raw = json_encode($sorted_env);
$signature = \Sodium\crypto_sign_detached($raw, $sign_key);
$data['sign'] = rtrim(base64_encode($signature), "=");
```

## Відправка даних

1. Додавання нових записів до ЦБД відбувається методом `PUT`  або `POST` запитом на URL колекції даних: https://api-sandbox.dozorro.org/api/v1/data
2. ЦБД приймає тільки підписані дані що мають вірно порахований `id` та відповідають схемі даних зазначених в `envelope.model` та `envelope.schema`;
3. ЦБД (на прод.) не прийматиме даних з датою створення старшою за за 1 добу в минулому або 1 хвилину в майбутньому.

#### Приклад

Візміть будь-який приклад [dozorro-schemas] / examples, підпишіть своїм ключем за допомогою [dozorro-keytool] та відправте за допомогою curl:

    $ python3 admin-keytool.py sign example-tender101.json

    $ curl -X PUT -H "Content-type: application/json" --data @example-tender101.json \
      https://api-sandbox.dozorro.org/api/v1/data

    {"created": 1}

## Корисні посилання

1. Схеми даних та приклади заповнення [dozorro-schemas]
2. Утиліта генерації ключів та підпису [dozorro-keytool]
3. Документація по формам [jsonform-wiki]
4. Dozorro JSON Form [Playground]
5. Перелік сторонніх [бібліотек](https://download.libsodium.org/doc/bindings_for_other_languages/) для розрахунку підпису.


---
&copy; 2016-2017 Volodymyr Flonts

[dozorro-schemas]: https://github.com/dozorro/dozorro-schemas
[dozorro-keytool]: https://github.com/dozorro/dozorro-keytool
[json-schema]: (http://json-schema.org/)
[jsonform-wiki]: https://github.com/joshfire/jsonform/wiki
[playground]: http://jsonform.ed.org.ua/


