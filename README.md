# provider-tom05

Provider OpenAI-compatible lokal untuk identitas **Tom05 flash Free**.

## Isi

- `server.py` — endpoint `/v1/models` dan `/v1/chat/completions` di `127.0.0.1:8772`.
- `provider.json` — metadata provider dan model.

## Konfigurasi OpenCode

```jsonc
{
  "providers": {
    "tom05": {
      "name": "Tom05",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "http://127.0.0.1:8772/v1" },
      "models": {
        "tom05-flash-free": { "name": "Tom05 flash Free", "modelID": "hy4-flash-free" }
      }
    }
  }
}
```

## Lisensi

Kode dalam repository ini tunduk pada **GNU Affero General Public License v3.0**
(lihat `LICENSE`). Lisensi IT Agenty `Tom05ivier-commits-1.0` tetap berlaku
untuk karya IT Agenty di workspace, bukan untuk kode di repository ini.
Tidak ada kredensial yang disimpan di sini.
