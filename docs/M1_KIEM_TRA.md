# M1 – Kinh tế cốt lõi: hướng dẫn cài và kiểm tra

Nhánh `m1-kinh-te` (đã gồm cả M0).

## Có gì mới

| Tính năng | Chi tiết |
|---|---|
| **Shop tính giá thật** | Gói thẻ = giá trị trung bình × 1,3 (mua 10 giảm 5%). Thẻ EXP, đổi tên, tuyển staff có giá |
| **Gỡ món "in tiền"** | Lucky EP, Jackpot, Peti EP, EP +…, hộp quà có giải EP, gói tháng, gói chuỗi, combo chứa EP, **đổi CLB**. Lệnh mua thẳng cũng bị chặn |
| **Món đã có trong kho / túi đồ** | Vẫn dùng bình thường |
| **Thưởng trận** | (thắng 8.000 / hòa 4.000 / thua 2.000) × hệ số độ khó + 500/bàn (tối đa 5) + 1.000 nếu sạch lưới |
| **Hệ số độ khó** | League mức 1 ×0,5 … mức 10 ×2,0, Tối thượng 1–5 ×2,3 → ×3,5; Cup ×0,5 / 0,8 / 1,2 / 1,8 / 2,5 |
| **EXP** | EXP HLV và cầu thủ cũng nhân hệ số độ khó |
| **Chế độ Manager** | 50% thưởng |
| **Thưởng mùa giải** | × độ khó; tự đá dưới 50% số trận thì giảm theo tỉ lệ (thấp nhất 20%) |
| **Thưởng Cup** | × độ khó |
| **Mở khóa theo cấp HLV** | League: cấp 1 → mức 1–3, cấp 5 → 5, cấp 10 → 7, cấp 20 → 10, cấp 35/50/70 → Tối thượng 2/4/5. Cup: cấp 1 → Bán chuyên, 10 → Chuyên nghiệp, 35 → Đẳng cấp, 70 → Huyền thoại |
| **Quán net / VIP** | Cấp 20: giảm 20% phí chợ + Scout quán net. Cấp 50: thêm 30% + Scout VIP |
| **Scout** | Có thời gian chờ: Scout chuyên nghiệp 6 giờ, quán net 6 giờ, VIP 12 giờ |
| **Trận** | 6 phút mỗi hiệp, thử 5 lượt thay người / 7 dự bị |
| **Điểm danh** | 3k → 20k EP + gói Thường (ngày 7: 20k + MF 65+) |
| **EP khởi đầu** | HLV mới: 50.000 EP. **Save cũ giữ nguyên EP** |
| **Mô phỏng kinh tế** | `python -I Server\tools\economy_sim.py --weekend-hours 1.5` |

Mọi con số nằm trong `Server/gamedata/config.json` (tự tạo khi chạy lần đầu), sửa xong khởi động lại server.

## Cài đặt

1. Tải nhánh `m1-kinh-te` (**Code → Download ZIP**), chép đè vào thư mục game.
2. **Nếu đã có `Server/gamedata/config.json` từ bản M0: xóa file đó** để server tạo lại bản có đủ mục mới.
3. Chạy `2_Choi_Game_Offline.bat`.

## Kiểm tra (~30 phút)

1. **Shop**
   - [ ] Các gói có giá (không còn 0 EP), mua thử 1 gói → EP bị trừ đúng giá
   - [ ] Không còn Lucky EP, hộp quà, gói tháng, gói chuỗi, đổi CLB
   - [ ] Tab Dapat dikonsumsi / Paket / MP Shop / Special Bonus không bị lỗi
2. **League**
   - [ ] Màn tạo mùa giải chỉ cho chọn 3 mức đầu (HLV dưới cấp 5)
   - [ ] Đá 1 trận: EP nhận được khớp công thức (ví dụ mức 3 thắng 2-0 = 8.000×0,8 + 1.000 + 1.000 = 8.400)
3. **Cup**
   - [ ] Chọn độ khó Chuyên nghiệp trở lên → bị từ chối (ghi lại thông báo hiện ra)
4. **Trận đấu**
   - [ ] Mỗi hiệp 6 phút
   - [ ] Thay được người thứ 4 và thứ 5 không; ghế dự bị có 7 người không
5. **Không có VIP** (HLV dưới cấp 20)
   - [ ] Màn chợ chuyển nhượng, Danh sách bán, Scout mở được, không lỗi
   - [ ] Scout chỉ còn 2 (Nghiệp dư, Chuyên nghiệp)
6. Đá thêm vài trận nếu được, rồi gửi lại:
   - `Server/captures/match_stats.jsonl`
   - `Server/captures/http_config.log`
   - `launcher_log.txt`
   - Ảnh chụp màn hình chỗ nào lạ (nhất là khi thay người / màn Scout / chợ)

## Nếu cần quay lại như cũ

- Thay người lỗi: sửa `"match": {"subs": 3, "bench": 5}` trong `config.json`.
- Màn nào hỏng vì tắt VIP: đặt `"unlocks": {"igr_level": 1, "vip_level": 1}`.
- Save: `python Server\career\save.py restore` (bản `..._truoc-nang-cap.json` là save trước M1).
