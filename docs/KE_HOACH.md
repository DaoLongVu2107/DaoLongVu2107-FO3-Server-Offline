# KẾ HOẠCH: FO3 OFFLINE – BẢN HOÀN CHỈNH (CHẾ ĐỘ SỰ NGHIỆP)

> Tài liệu sống, cập nhật theo tiến độ. Mọi con số là bản nháp, chốt bằng công cụ mô phỏng ở M10.

## 1. Tầm nhìn

Game bóng đá offline một người chơi, **cày ~300 giờ**: bắt đầu từ hạng thấp, kiếm EP, săn thẻ hiếm,
nâng +10, leo lên đỉnh châu Âu. **Không cheat, không sandbox, không paywall** – mọi thứ kiếm được bằng chơi.
Gameplay xoay quanh **vòng lặp mùa giải**.

## 2. Các quyết định đã chốt

| Chủ đề | Quyết định |
|---|---|
| Sandbox | Không có. Cheat chỉ bật khi chạy `FO3_DEV=1` (để test) |
| Thời lượng cày | ~300 giờ để đạt đỉnh |
| Đội khởi đầu | **Bắt buộc bắt đầu ở hạng thấp**, leo dần lên |
| Thời lượng trận | Giống FIFA/FC hiện tại: **6 phút mỗi hiệp** (`halfLength = 60`), thử 5 lượt thay người / 7 dự bị |
| Thẻ hiếm | Có từ **sự kiện**, **mua bằng EP** (đắt), hoặc **hên lắm rơi từ trận** |
| Bảo hiểm rơi thẻ | **Có** – sau 300 trận thắng không ra Huyền thoại thì lần sau chắc chắn ra |
| Phong độ cầu thủ | **Có, ngẫu nhiên** theo loại thẻ (xem 3.6) |
| Đấu hạng | **Bỏ** – thay bằng vòng lặp mùa giải |
| Kỳ chuyển nhượng | **Theo giờ thật**; đặt lệnh lúc nào cũng được, chỉ khớp trong kỳ |
| Bot CLB | **Tự mua bán cầu thủ bất kỳ** |
| Lịch người chơi | Đi làm thứ 2–6 (chơi ~30 phút buổi tối), nghỉ thứ 7, CN (≥ 1 giờ/ngày) |

Ước tính: tối thiểu ~4,5 giờ/tuần → 300 giờ ≈ 15 tháng; chơi cuối tuần 3 giờ/ngày → ≈ 8 tháng.

## 3. Các hệ thống

### 3.1 Nền móng
- `gamedata/config.json`: mọi con số cân bằng.
- Đánh số phiên bản save + tự nâng cấp save; tự sao lưu mỗi lần mở (giữ 10 bản).
- Chế độ DEV (`FO3_DEV=1`): bật lại công cụ cheat để test.
- Test tự động + công cụ mô phỏng kinh tế 300 giờ.
- Launcher: kiểm tra phiên bản Python, cổng 443, script gỡ dòng hosts.
- Chống chỉnh giờ (nhẹ): phát hiện giờ máy bị lùi → không phát thêm quà / phiên khớp lệnh.

### 3.2 Hai đồng hồ

| Đồng hồ | Điều khiển |
|---|---|
| **Giờ thật** (giờ máy, UTC+7) | Kỳ chuyển nhượng, phiên khớp lệnh, nhiệm vụ ngày/tuần, quà đăng nhập, giờ vàng, sự kiện ngày lễ, phong độ hằng tuần |
| **Lịch mùa giải** (chạy theo số trận đã đá) | Vòng League, cúp, lên/xuống hạng, tổng kết mùa |

### 3.3 Sự nghiệp HLV và mở khóa (nháp)

| Cấp HLV | Mở khóa |
|---|---|
| 1 | League hạng thấp, AI Nghiệp dư/Bán chuyên, shop gói Thường |
| 10 | AI Chuyên nghiệp, nhiệm vụ tuần |
| 20 | Đặc quyền "VIP 1" (giảm phí chợ) |
| 35 | AI Đẳng cấp, shop gói Hiếm |
| 50 | "VIP 2", shop xoay vòng (Huyền thoại, giới hạn lượt) |
| 70 | AI Huyền thoại, đội tuyển quốc gia |
| 100 | Danh hiệu, thưởng lớn |

### 3.4 Kinh tế EP
- Khởi đầu ~50.000 EP; tắt `SHOP_FREE`; gỡ các gói "in tiền" (+1 triệu EP, Lucky EP 50 triệu…).
- **Nguồn thu:** trận đấu (× hệ số độ khó AI), mùa giải, cúp, nhiệm vụ, sự kiện, bán cầu thủ.
- **Trận mô phỏng:** ~30% thưởng, giới hạn số trận/ngày, không rơi đồ.
- **Nơi tiêu:** chợ, gói thẻ, nâng cấp (+1…+10), phí chợ.
- Xóa paywall: VIP → theo cấp HLV; cash shop → bỏ; MP Shop → Shop Thành tích; gói tháng → mua bằng EP; gói chuỗi → chuỗi nhiệm vụ.

### 3.5 Định giá thẻ (hiệu chỉnh bằng dữ liệu fifaaddict)

Dữ liệu: 38.098 thẻ (16.035 có giá KR, 10.452 có giá VN) – `tools/fa_sync.py`.

```
Giá gốc = Đường cong OVR (~×1,2 / OVR)
        × Hệ số mùa      (median theo mùa, NÉN: UL ×213 → ~×6,5; '07 ×0,07 → ~×0,4)
        × Hệ số ngôi sao (internationalrep 4–5 sao: VN ×4,2 / ×19 → nén ~×1,5 / ×2,5)
        × Hệ số meta     (tốc độ/khéo léo: chỉ ±10%, tương quan dữ liệu chỉ +0,12)
        × Hệ số cấp thẻ  (+1…+10)
```

- Bỏ thiên vị quốc tịch của server Hàn (cầu thủ Hàn ×11,6).
- `card_price` cũ giữ nguyên cho Scout/nâng cấp/gói; chợ dùng `market_price` riêng.
- Sổ tay HLV cho sửa tay hệ số mùa / giá từng thẻ.

**Hệ số mùa (KR, median so với thẻ cùng OVR):** UL ×213 · EL ×41 · UB ×38 · WL ×17 · 16EC ×13 · MUA ×11 ·
WB ×10 · CC ×9 · KL02 ×7 · 14WC ×4,4 · 14T ×3,4 · LP ×3,3 · CP ×2,9 · 06U ×2 · 10U ×1,6 · '11 ×1,2 · '15 ×1 ·
10WC ×0,8 · '17 ×0,7 · 06WC ×0,6 · 08E ×0,25 · '06–'10 ×0,07–0,2.

### 3.6 Phát triển cầu thủ và phong độ
- Cấp độ (tối đa 23) qua trận + thẻ EXP (mua bằng EP / thưởng).
- Nâng cấp +1…+10 giữ tỉ lệ hiện có; là nơi tiêu EP lớn nhất cuối game.
- **Phong độ ngẫu nhiên** (đổi mỗi thứ 2 theo giờ thật), thực hiện bằng cách tạm đổi cấp thẻ gửi vào trận (cần test):

| Loại thẻ | Phong độ |
|---|---|
| Thẻ yếu (OVR thấp, mùa Thường) | Dao động mạnh, đôi khi bùng nổ / tụt |
| Trẻ (≤ 21 tuổi theo mùa thẻ) | Thiên về tăng; có cơ hội phát triển vĩnh viễn sau mỗi mùa |
| Già (≥ 33 tuổi) | Thiên về giảm |
| Icon (Huyền thoại/Thần thoại) | Ổn định |

- Phong độ ảnh hưởng giá chợ; bot cũng có phong độ.

### 3.7 Bậc thẻ và gói thẻ

| Bậc | Mùa | Cách có |
|---|---|---|
| Thường | '06–'10, '14, '15, '16, '17, 16TH, 17TH, U23, KXI, VS, 06WC, 08E, 10WC | Shop EP, thưởng trận, quà ngày |
| Hiếm | '11, 14WC, 14T, 06U, 10U, LP, CP | Shop EP (đắt), nhiệm vụ tuần, rơi trận 3% |
| Huyền thoại | 16EC, CC, KL02, TCO92, CL, ML, TL, VL, WB | Sự kiện, thưởng cúp lớn, shop xoay vòng, rơi trận 0,5% |
| Thần thoại | WL, EL, CEL, MUA, MUL, UB, UL | Sự kiện ngày lễ lớn, vô địch C1/CWC, rơi trận 0,1% |

- Mỗi mùa 3 loại gói: "Mùa X" / "Top 50" / "Top 10" (Top 10 = bậc cao hơn 1 bậc). Bản +3/+5/+8 chỉ từ sự kiện.
- Giá gói = giá trị trung bình × 1,2–1,5 (mở gói là cược; mua lẻ ở chợ kinh tế hơn).
- Bỏ giới hạn bản quyền server ID trong gói.

### 3.8 Thế giới và mùa giải
- `gamedata/world.json`: đội hình hiện tại của 501 CLB (33 giải, 19 quốc gia).
- Kim tự tháp: Anh 4 hạng, Đức 3, Tây Ban Nha/Pháp/Ý 2, các nước khác 1. Top 3 lên, 3 cuối xuống.
- League 20 đội / 38 vòng nếu giao diện cho phép (cần test), không thì 10 đội / 18 vòng.
- Các giải khác mô phỏng song song; bot cũng lên/xuống hạng, giành suất châu lục.
- Tổng kết mùa: giải thưởng cá nhân, suất châu lục, ban lãnh đạo chấm điểm.
- Cầu thủ không già đi (chỉ số nằm trong DB của client) – bù bằng phong độ + chuyển nhượng.

### 3.9 Cúp

| Cúp | Dự | Thể thức |
|---|---|---|
| Cúp quốc gia | Mọi CLB trong nước | Loại trực tiếp |
| Siêu cúp quốc gia | VĐQG vs Cúp QG | 1 trận |
| Cúp C1 châu Âu | Top 1–4 giải lớn | Vòng bảng + loại trực tiếp |
| Cúp C2 | Hạng 5–6 + đội bị loại ở vòng bảng C1 | Vòng bảng + loại trực tiếp |
| Cúp C3 | Hạng 7 + vô địch giải nhỏ | Vòng bảng + loại trực tiếp |
| Siêu cúp châu Âu | Vô địch C1 vs C2 | 1 trận |
| Cúp Nam Mỹ / châu Á | CLB các nước tương ứng | Như C1 |
| Cúp thế giới các CLB | Vô địch các châu lục | 8 đội loại trực tiếp |

- Cách 1 (làm trước): dựa trên chế độ Cup có sẵn, chỉ hiện cúp đủ điều kiện mùa này. 16 đội; thử 32.
- Cách 2 (thử nghiệm): cúp lồng trong League gốc (`cupqualifier`/`cupfinal`).
- Dùng tên thường gọi ("Cúp C1 châu Âu"…), không dùng tên/logo thương hiệu chính thức.

### 3.10 Kỳ chuyển nhượng, chợ và bot

**Lịch (giờ thật, chỉnh được trong config):**

| Kỳ | Thời gian |
|---|---|
| Cuối tuần | 19h thứ 6 → 23h59 Chủ nhật |
| Giữa tuần | Thứ 4, 19h–23h |
| Kỳ hè lớn | Tháng 6–8: hàng gấp đôi, nhiều bom tấn |
| Kỳ đông lớn | Tháng 1 |

**Sổ lệnh:**
- Đặt lệnh mua (EP bị giữ) / lệnh bán lúc nào cũng được; chỉ khớp trong kỳ, mỗi 2 giờ một phiên (tính bù khi mở game).
- Cơ hội khớp theo giá đặt / giá chợ: mua ≥ 100% hoặc bán ≤ 95% → khớp ngay; xa dần → 50% / 15% / 3% mỗi phiên;
  mua < 70% hoặc bán > 130% → giá ảo, không nhận.
- Chưa khớp → chuyển sang kỳ sau; sau 3 kỳ → hết hạn (hoàn EP / trả cầu thủ qua túi đồ).
- Cầu thủ đang rao bán vẫn đá cho bạn tới khi hoàn tất (cần test).
- Giá chợ = giá gốc × (xu hướng riêng + dao động ngày + cung cầu + sự kiện + phong độ), giới hạn 0,7–1,4×.

**Bot CLB:** ngân sách theo uy tín/hạng/thành tích; nhu cầu theo vị trí; tính cách (bom tấn, mua rẻ bán đắt,
mê thẻ cổ…); mua bất kỳ thẻ nào theo ngân sách; một cầu thủ chỉ ở 1 CLB bot; bot hỏi mua cầu thủ của bạn;
hàng trên chợ đến từ bot; bản tin chuyển nhượng.

### 3.11 Nhiệm vụ, thành tích, rơi đồ

| Loại | Ngày thường (thứ 2–6) | Cuối tuần (thứ 7, CN) |
|---|---|---|
| Nhiệm vụ ngày | 3 nhiệm vụ ngắn (xong trong 1–2 trận) | 8–10 nhiệm vụ, có nhiệm vụ khó |
| Thưởng | Nhỏ | Lớn (gói Hiếm/Huyền thoại, xu sự kiện) |
| Thêm | Quà đăng nhập | Giải cuối tuần, giờ vàng ×2 EP |

- Nhiệm vụ tuần: 12 (rương 4/8/12), hạn 23h59 CN. Nhiệm vụ tháng: 5. Chuỗi nhiệm vụ: ~10 chuỗi.
- Nhiệm vụ tồn: ngày thường chưa xong → dồn sang cuối tuần (tối đa 6). Chuỗi đăng nhập không đứt khi lỡ 1–2 ngày thường.
- Thành tích trọn đời 150+ (có ẩn) → Điểm thành tích → Shop Thành tích; huy hiệu HLV (cần test).
- Rơi đồ sau trận thắng tự đá: Thường 15% / Hiếm 3% / Huyền thoại 0,5% / Thần thoại 0,1%; bảo hiểm Huyền thoại sau 300 trận thắng.
- Tủ danh hiệu, Đại sảnh danh vọng (thống kê trọn đời từng thẻ), ban lãnh đạo CLB, nhà tài trợ.

### 3.12 Sự kiện, sưu tầm
- Lịch lễ theo giờ máy: Tết Dương, Valentine, 30/4, 2/9, Halloween, Noel; âm lịch: Tết Nguyên Đán, Trung Thu
  (bảng ngày tính sẵn ~10 năm); mùa World Cup, chung kết cúp châu Âu.
- Xu sự kiện + shop sự kiện (gói Thần thoại), quà đăng nhập, thưởng nhân đôi.
- Sự kiện ngẫu nhiên ("đêm bão giá", "nhà đầu tư ghé thăm"), cầu thủ của tuần.
- Album sưu tập, team color đặc biệt (Huyền thoại MU, Galácticos…), vòng quay may mắn (vé từ nhiệm vụ), đổi 5 thẻ → 1 gói bậc trên.

### 3.13 Team color
- Giữ cơ chế hiện có (CLB +1…+4, quốc gia/mùa +1…+3, không cộng dồn).
- Thêm team color đặc biệt (thưởng Album/sự kiện), team color cho bot theo độ khó (cần test),
  ảnh hưởng nhu cầu chợ, gợi ý mua trong Sổ tay, Việt hóa mô tả.

### 3.14 Sổ tay HLV + Việt hóa
- Trang admin → Sổ tay HLV tiếng Việt: thống kê, bảng xếp hạng mọi giải, nhánh cúp, sổ lệnh, biểu đồ giá,
  bản tin chuyển nhượng, nhiệm vụ, Album, team color, sao lưu/khôi phục, cài đặt. Không có nút cheat.
- Việt hóa chữ do server gửi (tên gói, tin nhắn túi đồ, nhiệm vụ…). Không sửa `language.big` của client.

### 3.15 Đội tuyển quốc gia
World Cup mỗi 4 mùa; EURO / Copa América xen giữa; bạn dẫn đội tuyển tự chọn.

### 3.16 Phát hành
Số phiên bản, `CHANGELOG`, ZIP cập nhật chỉ chứa phần thay đổi, hướng dẫn tiếng Việt.
Phần mới tách module riêng (`economy.py`, `market.py`, `world.py`, `events.py`…) để dễ gộp bản cập nhật của tác giả gốc.

## 4. Lộ trình

| Mốc | Nội dung | Test trong game |
|---|---|---|
| M0 | Nền móng (3.1) + mô phỏng kinh tế | 0–1 |
| M1 | Kinh tế cốt lõi, mở khóa theo cấp, khóa cheat, thời lượng trận (3.3, 3.4) | 1 |
| M2 | Định giá thẻ + gói thẻ theo bậc + dữ liệu fifaaddict (3.5, 3.7) | 1 |
| M3 | Thế giới & mùa giải: `world.json`, kim tự tháp, lên/xuống hạng, bắt đầu hạng thấp (3.8) | 2–3 |
| M4 | Kỳ chuyển nhượng giờ thật, sổ lệnh, chợ sống, bot mua bán, phong độ (3.6, 3.10) | 2–3 |
| M5 | Cúp: quốc gia, siêu cúp, C1/C2/C3, CWC (3.9) | 2–3 |
| M6 | Nhiệm vụ theo nhịp tuần, thành tích, rơi đồ + bảo hiểm, tủ danh hiệu, ban lãnh đạo (3.11) | 2 |
| M7 | Sự kiện ngày lễ, Album, team color đặc biệt, vòng quay, đổi thẻ (3.12, 3.13) | 2 |
| M8 | Sổ tay HLV + Việt hóa (3.14) | 1 |
| M9 | Đội tuyển quốc gia (3.15) | 3–5 |
| M10 | Cân bằng 300 giờ + bản 1.0 (3.16) | Chơi thật |

Mỗi mốc một nhánh riêng; gộp vào `main` sau khi test trong game.

## 5. Cần test trong game (rủi ro)
1. Đội bot có cầu thủ CLB/mùa khác hiển thị đúng.
2. League 20 đội.
3. Thông báo khi chợ đóng / lệnh đặt trước từ nút "Mua" trong game.
4. Cầu thủ đang rao bán vẫn ở trong đội hình.
5. Phong độ qua cấp thẻ tạm thời trong trận.
6. 5 lượt thay người / 7 dự bị.
7. Team color cho bot; huy hiệu HLV; Cup 32 đội; cúp lồng trong League.
8. Ghi toàn bộ dữ liệu `matchStats` để mở thêm loại nhiệm vụ.

## 6. Đầu việc và tiến độ

Kích thước: S ≈ 0,5 · M ≈ 1 · L ≈ 2–3 · XL ≈ 4–5 phiên làm việc. 🎮 = cần test trong game.

### M0 – Nền móng (~5 phiên · 1 lượt test) — nhánh `m0-nen-mong`, xem [M0_KIEM_TRA.md](M0_KIEM_TRA.md)
- [x] 0.1 Tách module mới (`config.py`, `economy.py`…), không phá code gốc — M
- [x] 0.2 `gamedata/config.json` + bộ đọc cấu hình có giá trị mặc định — S
- [x] 0.3 Đánh số phiên bản save + khung nâng cấp save — M
- [x] 0.4 Tự sao lưu save mỗi lần mở (giữ 10 bản) + khôi phục — S
- [x] 0.5 Chế độ DEV (`FO3_DEV=1`) + khóa cheat trên trang admin — S
- [x] 0.6 Bộ test tự động (HLV giả, trận giả, giả lập thời gian) — M
- [x] 0.7 Ghi toàn bộ `matchStats` sau trận 🎮 — S *(code xong, chờ test trong game)*
- [x] 0.8 Launcher: kiểm tra Python, cổng 443, script gỡ hosts — S *(code xong, chờ test trong game)*
- [x] 0.9 Phát hiện giờ máy bị lùi — S

### M1 – Kinh tế cốt lõi (~5 phiên · 1 lượt test)
- [ ] 1.1 Tắt shop miễn phí, giá shop thật, EP khởi đầu 50k — S
- [ ] 1.2 Gỡ/sửa các gói "in tiền" — S
- [ ] 1.3 Thưởng trận theo độ khó AI + thưởng bàn thắng — M
- [ ] 1.4 Giới hạn trận mô phỏng — S
- [ ] 1.5 Mở khóa theo cấp HLV — M
- [ ] 1.6 Đặc quyền VIP theo cấp — S
- [ ] 1.7 Trận 6 phút/hiệp + thử 5 lượt thay / 7 dự bị 🎮 — S
- [ ] 1.8 Công cụ mô phỏng kinh tế (bản đầu) — M

### M2 – Định giá thẻ và gói thẻ (~5 phiên · 1 lượt test)
- [ ] 2.1 Đưa dữ liệu fifaaddict vào repo — S
- [ ] 2.2 `market_price`: OVR × mùa × ngôi sao × meta (có nén) — M
- [ ] 2.3 Bảng hệ số mùa + bậc mùa — S
- [ ] 2.4 Gói theo mùa "Mùa X" / "Top 50" / "Top 10" — M
- [ ] 2.5 Bỏ giới hạn bản quyền server ID trong gói — S
- [ ] 2.6 Xếp gói cũ vào bậc, shop theo cấp mở khóa — M
- [ ] 2.7 Kiểm tra shop và mở gói trong game 🎮 — S

### M3 – Thế giới và mùa giải (~11 phiên · 2–3 lượt test)
- [ ] 3.1 `world.json`: đội hình 501 CLB — M
- [ ] 3.2 Đội bot lấy từ `world.json` 🎮 — M
- [ ] 3.3 Kim tự tháp giải đấu — M
- [ ] 3.4 Bắt đầu ở hạng thấp nhất 🎮 — M
- [ ] 3.5 Thử League 20 đội / 38 vòng 🎮 — M
- [ ] 3.6 Lên/xuống hạng giữa các hạng thật — M
- [ ] 3.7 Mô phỏng các giải khác song song — M
- [ ] 3.8 Tổng kết mùa, chuyển mùa mới — L
- [ ] 3.9 Mục tiêu ban lãnh đạo — M

### M4 – Kỳ chuyển nhượng, chợ và bot (~12 phiên · 2–3 lượt test)
- [ ] 4.1 Lịch kỳ chuyển nhượng theo giờ thật — S
- [ ] 4.2 Giá chợ động — M
- [ ] 4.3 Sổ lệnh (mua giữ EP, bán, hủy, hết hạn) — L
- [ ] 4.4 Phiên khớp lệnh mỗi 2 giờ + tính bù — M
- [ ] 4.5 Gắn vào màn hình chợ của game 🎮 — M
- [ ] 4.6 Cầu thủ đang rao bán vẫn trong đội hình 🎮 — S
- [ ] 4.7 Bot CLB mua bán (ngân sách, nhu cầu, tính cách) — L
- [ ] 4.8 Bot hỏi mua cầu thủ của bạn — M
- [ ] 4.9 Phong độ ngẫu nhiên theo loại thẻ 🎮 — M
- [ ] 4.10 Phát triển vĩnh viễn cho thẻ trẻ — S

### M5 – Cúp (~9 phiên · 2–3 lượt test)
- [ ] 5.1 Mở rộng chế độ Cup, chỉ hiện cúp đủ điều kiện — M
- [ ] 5.2 Cúp quốc gia — M
- [ ] 5.3 C1 / C2 / C3 + suất dự theo mùa trước — L
- [ ] 5.4 Siêu cúp quốc gia, Siêu cúp châu Âu 🎮 — S
- [ ] 5.5 Cúp Nam Mỹ / châu Á + Cúp thế giới các CLB — M
- [ ] 5.6 Tiền thưởng theo vòng — S
- [ ] 5.7 Thử C1 32 đội 🎮 — M

### M6 – Nhiệm vụ, thành tích, rơi đồ (~12 phiên · 2 lượt test)
- [ ] 6.1 Bộ máy nhiệm vụ — L
- [ ] 6.2 Kho ~80 mẫu + nhịp tuần — M
- [ ] 6.3 Nhiệm vụ tuần / tháng / chuỗi — M
- [ ] 6.4 Nhiệm vụ tồn + chuỗi đăng nhập không đứt — S
- [ ] 6.5 Thành tích 150+ + Shop Thành tích — L
- [ ] 6.6 Rơi đồ + bảo hiểm — S
- [ ] 6.7 Giờ vàng, giải cuối tuần — M
- [ ] 6.8 Tủ danh hiệu, Đại sảnh danh vọng, nhà tài trợ — M
- [ ] 6.9 Huy hiệu HLV 🎮 — S

### M7 – Sự kiện và sưu tầm (~9 phiên · 2 lượt test)
- [ ] 7.1 Lịch lễ dương + âm — S
- [ ] 7.2 Bộ máy sự kiện (xu, shop, quà, nhân thưởng) — L
- [ ] 7.3 ~10 sự kiện ngày lễ — M
- [ ] 7.4 Sự kiện ngẫu nhiên + cầu thủ của tuần — S
- [ ] 7.5 Album sưu tập — M
- [ ] 7.6 Team color đặc biệt + cho bot 🎮 — M
- [ ] 7.7 Vòng quay + đổi 5 thẻ lấy 1 gói — M

### M8 – Sổ tay HLV và Việt hóa (~6 phiên · 1 lượt test)
- [ ] 8.1 Khung Sổ tay HLV — M
- [ ] 8.2 Bảng xếp hạng, nhánh cúp, sổ lệnh, biểu đồ giá, bản tin — L
- [ ] 8.3 Nhiệm vụ, Album, team color + gợi ý, sao lưu, cài đặt — M
- [ ] 8.4 Việt hóa chữ do server gửi 🎮 — M

### M9 – Đội tuyển quốc gia (~7 phiên · 3–5 lượt test)
- [ ] 9.1 Tìm hiểu màn World Cup của game qua log 🎮 — L
- [ ] 9.2 Đội tuyển ghép theo quốc tịch — M
- [ ] 9.3 World Cup / EURO / Copa América theo chu kỳ — L
- [ ] 9.4 Dự phòng: dạng Cup thường — S

### M10 – Cân bằng và bản 1.0 (~5 phiên · chơi thật)
- [ ] 10.1 Mô phỏng 300 giờ, chỉnh số — M
- [ ] 10.2 Sửa lỗi khi chơi thật — L
- [ ] 10.3 CHANGELOG, ZIP cập nhật, hướng dẫn — S

**Tổng:** ~86 phiên code · ~17–22 lượt test · ~3–4 tháng (khoảng 2 lượt test/tuần).
