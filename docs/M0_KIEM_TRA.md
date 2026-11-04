# M0 – Nền móng: hướng dẫn cài và kiểm tra

## Có gì mới

| Tính năng | Bạn thấy gì |
|---|---|
| **Khóa cheat** | Trang admin (http://127.0.0.1:8088) không còn chỉnh được EP, cầu thủ, gói, quà. Xem thông tin và chuyển cầu thủ đội chính ↔ dự bị vẫn dùng được |
| **Chế độ DEV** | Chạy `3_Choi_Che_Do_DEV.bat` để bật lại cheat khi cần test. Trang admin hiện nhãn đỏ **CHẾ ĐỘ DEV** |
| **Tự sao lưu save** | Mỗi lần mở server, save được chép vào `Server/gamedata/backups/` (giữ 10 bản; save không đổi thì không chép thêm) |
| **Phiên bản save** | Save được gắn số phiên bản (hiện là 1), sau này tự nâng cấp khi có bản mới |
| **Ghi khoá an toàn** | Save được ghi qua file tạm, mất điện lúc đang lưu cũng không hỏng save |
| **File cấu hình** | `Server/gamedata/config.json` tự tạo lần đầu chạy |
| **Ghi dữ liệu trận** | Mỗi trận kết thúc được ghi vào `Server/captures/match_stats.jsonl` |
| **Kiểm tra trước khi chạy** | Launcher báo phiên bản Python và cổng 443 / 8088 / 28002 có bị chiếm không |
| **Gỡ hosts** | `4_Go_Cai_Dat_Hosts.bat` (chạy bằng quyền Administrator) xóa dòng `APSEODESK172` |
| **Chống lùi giờ** | Chỉnh giờ máy lùi lại thì quà đăng nhập tạm dừng tới khi giờ chạy qua mốc cũ |

## Cài đặt

1. Tải nhánh `m0-nen-mong` (GitHub → chọn nhánh → **Code → Download ZIP**).
2. Chép đè **toàn bộ** vào thư mục game (nơi có `fifazf.exe`), chọn ghi đè.
3. Không cần chạy lại `1_Cai_Dat_Hosts.bat`.

## Kiểm tra (~20–30 phút)

1. Chạy `2_Choi_Game_Offline.bat`.
   - [ ] Có dòng `[*] Kiem tra truoc khi chay...` và các dòng `[OK] ...` (Python, cổng 443…)
   - [ ] Cửa sổ "FO3 Offline Server" có các dòng `[career] ...` (config, sao lưu, phiên bản save)
   - [ ] Vào game bình thường, đội hình và EP như cũ
2. Đá **1 trận League** và **1 trận Cup** đến hết trận.
3. Mở http://127.0.0.1:8088
   - [ ] Có dòng thông báo "Chế độ Sự nghiệp: các công cụ … đã bị khóa"
   - [ ] Bấm "Add EP" → báo "Da khoa trong che do Su nghiep…"
4. (Tùy chọn) Tắt server, chạy `3_Choi_Che_Do_DEV.bat` → trang admin có nhãn **CHẾ ĐỘ DEV**, các nút dùng lại được.

## Gửi lại cho mình

- `Server/captures/match_stats.jsonl` (dữ liệu 2 trận vừa đá)
- `launcher_log.txt` (trong thư mục game)
- Ảnh hoặc mô tả nếu có gì lạ

## Khôi phục save khi cần

Tắt server, rồi chạy trong thư mục game:

```bat
python Server\career\save.py restore
```

Chọn số bản sao lưu. Save hiện tại được giữ lại với tên `..._truoc-khoi-phuc.json`.

## Chạy test tự động (không cần game)

```bat
python -I Server\tests\run_all.py
```

Cần giải nén `Server\gamedata\fifadb.rar` trước để chạy đủ 26 test.
