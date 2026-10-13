# API Notes — MyMemory Translation API

## 1. Overview and Endpoint

- **Service Name:** MyMemory Translation API
- **Provider:** Translated (translated.net)
- **API Base Endpoint:** `https://api.mymemory.translated.net/get`
- **Protocol:** HTTPS GET
- **Official Documentation:** [https://mymemory.translated.net/doc/spec.php](https://mymemory.translated.net/doc/spec.php)

---

## 2. Request Parameters

| Parameter | Type | Required? | Description |
| :--- | :--- | :--- | :--- |
| `q` | String | **Yes** | The source text to translate (UTF-8 encoded, max ~500 characters per request). |
| `langpair` | String | **Yes** | Source and target language pair separated by `\|` (e.g. `en\|ur`, `ur\|en`, or `autodetect\|en`). |
| `de` | String | *Optional* | Contact email address. Supplying an email raises the daily free quota from 5,000 to **50,000 characters/day**. |
| `mt` | Integer | *Optional* | Machine Translation flag (`1` enables machine translation fallback, `0` disables it). Default is `1`. |
| `key` | String | *Optional* | Private API key for private translation memories (not required for public free use). |

### Example Request URL:
```http
GET https://api.mymemory.translated.net/get?q=Hello+world&langpair=en|ur&de=student@example.com
```

---

## 3. Response Structure

The API returns a JSON payload:

```json
{
  "responseData": {
    "translatedText": "ہیلو دنیا",
    "match": 0.85,
    "detectedLanguage": "en"
  },
  "quotaFinished": false,
  "mtLangSupported": null,
  "responseDetails": "",
  "responseStatus": 200,
  "matches": [
    {
      "id": 0,
      "segment": "Hello world",
      "translation": "ہیلو دنیا",
      "quality": 70,
      "reference": "Machine Translation.",
      "match": 0.85,
      "model": "neural"
    }
  ]
}
```

### Key Response Fields:
- `responseData.translatedText`: The resulting translation string. May contain HTML character entities (e.g., `&#39;`) which our engine automatically unescapes.
- `responseData.detectedLanguage`: Returned when `autodetect` is passed in `langpair`.
- `responseData.match`: Numerical quality match score between `0.0` and `1.0`.
- `responseStatus`: HTTP/API status integer (200 = Success, 403 = Forbidden, 429 = Quota exceeded, 500 = Server error).
- `quotaFinished`: Boolean indicating whether daily character allowance is exhausted.
- `responseDetails`: Human-readable status message or warning text.

---

## 4. Quotas, Rates, and Free Tier Conditions

- **Anonymous Public Usage:** Up to **5,000 characters per day** per IP address.
- **Free Usage with Email (`de` parameter):** Up to **50,000 characters per day**.
- **Credit Card Requirement:** **None.** No credit card or billing agreement is ever needed.
- **Single Request Character Limit:** 500 characters. To translate longer paragraphs, our engine implements sentence-level chunking up to a maximum safety threshold of 2,500 characters.

---

## 5. Verified Language Support

The following language pairs were verified directly against the live API:

- **English (`en`) ⇄ Urdu (`ur`)**: Fully verified. Supports Urdu Nastaliq and Arabic scripts, Right-to-Left formatting, and automatic detection.
- **Auto-Detection (`autodetect`)**: Verified. Accurately detects English (`en`), Urdu (`ur`), and other common scripts.
- **Additional Multilingual Support:** Arabic (`ar`), Spanish (`es`), French (`fr`), German (`de`), Hindi (`hi`), Chinese Simplified (`zh-CN`), Japanese (`ja`), Russian (`ru`), Turkish (`tr`), Italian (`it`), Portuguese (`pt`), Korean (`ko`), Persian (`fa`), Pashto (`ps`), Punjabi (`pa`), Bengali (`bn`).

---

## 6. Error Codes and Handling Strategy

| Status Code / Condition | Meaning | Application Handling |
| :--- | :--- | :--- |
| `200` | Success | Unescape HTML entities and display in UI with RTL/LTR styling. |
| `429` / `quotaFinished: true` | Daily quota exceeded | Catch with `RateLimitError` and display user-friendly message advising email configuration or daily reset. |
| `403` | IP blocked or forbidden | Catch with `RateLimitError`. |
| `500` / `502` / `503` | Server-side downtime | Catch with `APIResponseError`. |
| Network Timeout | No response in 10s | Catch with `RequestTimeoutError`. |
| No Internet | Connection aborted / DNS failure | Catch with `NetworkError`. |

---

## 7. Privacy, Terms of Use, and Limitations

1. **Public Translation Memory:** MyMemory is a collaborative translation memory. Sensitive credentials, confidential passwords, and personal financial data should **never** be transmitted.
2. **Chunking Trade-off:** When text exceeds 450 characters, splitting by sentences preserves grammatical integrity, but isolated sentences may lack broader paragraph context.
3. **Internet Dependency:** This tool requires an active internet connection to communicate with the MyMemory servers.
