import asyncio
import os


os.environ['BROWSER_USE_CDP_TIMEOUT_S'] = '360.0'
os.environ['TIMEOUT_ScreenshotEvent'] = '360.0'
os.environ['TIMEOUT_BrowserStateRequestEvent'] = '360.0'
os.environ['TIMEOUT_ClickElementEvent'] = '60.0'
os.environ['TIMEOUT_NavigateToUrlEvent'] = '60.0'

from browser_use import Agent, Browser, ChatOpenAI, Controller
from playwright.async_api import Page
import asyncio

controller = Controller()

@controller.action("Lấy danh sách TẤT CẢ các nhóm đã tham gia (an toàn, không bị treo máy)")
async def get_all_joined_groups(page: Page):
	print("⏳ Đang quét ngầm danh sách toàn bộ các nhóm đã tham gia...")
	await page.goto("https://www.facebook.com/groups/joins/")
	# Cuộn trang vài lần để load toàn bộ danh sách
	for _ in range(5):
		await page.evaluate("window.scrollBy(0, 3000)")
		await asyncio.sleep(1.5)
	
	groups = await page.evaluate(r'''() => {
		const links = Array.from(document.querySelectorAll('a[href*="/groups/"]'));
		const groupsObj = {};
		links.forEach(a => {
			const text = a.innerText.trim().split('\n')[0];
			if (text && a.href.match(/\/groups\/\d+\/?$/) && text.length > 3) {
				groupsObj[text] = a.href;
			}
		});
		return groupsObj;
	}''')
	
	# Quay về trang chủ để tránh DOMWatchdog bị kẹt khi đọc trang list nhóm
	await page.goto("https://www.facebook.com/")
	
	res = "Danh sách URL các nhóm đã tham gia (Hãy dùng lệnh navigate để truy cập từng URL):\n"
	count = 0
	for name, url in groups.items():
		res += f"{count+1}. {name}: {url}\n"
		count += 1
	print(f"✅ Đã quét được {count} nhóm!")
	return res


async def main():

	model_name = os.getenv('QWEN_MODEL', 'gemma32kcxt:latest')
	base_url = os.getenv('QWEN_BASE_URL', 'https://tuanphamai.online/v1')
	
	print(f"🚀 Đang khởi tạo LLM ({model_name}) tại {base_url}...")
	llm = ChatOpenAI(
		model=model_name,
		base_url=base_url,
		api_key='ollama',
		temperature=0.0,
		timeout=300.0,
		extra_body={'options': {'num_ctx': 65536}},
		default_headers={
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
		},
		max_completion_tokens=32768,
		dont_force_structured_output=True,
		add_schema_to_system_prompt=True,
	)

	print("🌐 Đang khởi tạo Browser sử dụng Chrome Profile 'Default' (Dương Việt)...")
	browser = Browser(
		executable_path='/usr/bin/google-chrome', 
		user_data_dir='/home/duongpv/.config/google-chrome', 
		profile_directory='Default', 
		headless=True, 
		window_size={'width': 1280, 'height': 800},
		viewport={'width': 1280, 'height': 800},
		args=[
			'--disable-blink-features=AutomationControlled',
			'--disable-infobars',
			'--disable-notifications',
			'--disable-popup-blocking',
		]
	)

	task = """
NHIỆM VỤ: Đăng bài (text + 2 video) lên TẤT CẢ hội nhóm Facebook — nhóm đã tham gia + nhóm mới.

QUY TẮC (TUYỆT ĐỐI TUÂN THỦ):
- Click thất bại → dùng go_back để refresh DOM, KHÔNG retry cùng index.
- 1 nhóm thất bại 2 lần → BỎ QUA ngay, chuyển nhóm tiếp.
- Nhóm "Đang chờ"/"Pending" → BỎ QUA.
- SAU KHI upload video xong → click nút "Đăng"/"Post" NGAY LẬP TỨC, không chờ thêm.

BƯỚC 1 - SWITCH PROFILE:
- Vào https://www.facebook.com → click avatar GÓC PHẢI → "See all profiles" → chọn "Ngọc Khuê Stem" → "Switch".
- Xác nhận avatar đã đổi.

BƯỚC 2 - ĐĂNG BÀI LÊN TẤT CẢ NHÓM ĐÃ JOIN (PHASE 1):
- GỌI HÀNG ĐỘNG `get_all_joined_groups` để lấy toàn bộ URL các nhóm đã tham gia.
- Dùng lệnh `navigate` để mở LẦN LƯỢT từng URL nhóm trong danh sách và đăng bài (Reels/Video).
- Đăng xong một nhóm, gọi lệnh `navigate` tới nhóm tiếp theo. KHÔNG bấm vào mục Groups ở menu trái nữa.

BƯỚC 3 - TÌM NHÓM MỚI VÀ ĐĂNG BÀI (PHASE 2):
- CHỈ làm bước này sau khi đã đăng xong HẾT các nhóm đã join.
- Dùng thanh tìm kiếm của Facebook, tìm MỖI LẦN 1 từ khóa: "lập trình scratch", "nhóm stem", "đồ án", "hỗ trợ các cuộc thi sáng tạo khoa học kĩ thuật", "giáo viên cấp 1", "giáo viên cấp 2".
- Chuyển sang tab "Nhóm" (Groups) trong kết quả.
- Bấm "Tham gia" (Join) vào các nhóm mới.
- Nếu được duyệt ngay → Đăng bài vào nhóm đó. Nếu "Đang chờ" (Pending) → BỎ QUA.

ĐĂNG REELS / BÀI VIẾT (cho mọi nhóm):
1. Ưu tiên tìm tab "Reels" (Thước phim) trong nhóm để đăng. Nếu không thấy "Reels", hãy bấm "Write something..." / "Bạn đang nghĩ gì?" ở tab Discussion.
2. Nhập văn bản: "Sản phẩm STEM học tập và sáng tạo."
3. Dùng lệnh upload_file để đẩy thẳng 2 video lên (KHÔNG bấm mở cửa sổ Ảnh/Video của hệ điều hành).
4. Phải đợi upload xong, kết thúc bước đó, rồi mới sang bước bấm Đăng. KHÔNG GỘP CHUNG VÀO 1 BƯỚC.
5. ĐỂ BẤM NÚT ĐĂNG: Bạn BẮT BUỘC dùng action `evaluate` với đoạn JS sau để ép click (không cần tìm index):
   code: "(function(){const b = Array.from(document.querySelectorAll('div[role=\"button\"]')).find(e => e.getAttribute('aria-label') === 'Post' || e.getAttribute('aria-label') === 'Đăng' || e.innerText.includes('Post') || e.innerText.includes('Đăng')); if(b) b.click();})()"
6. Đợi 5s xác nhận màn hình hiển thị "Processing video" (Đang xử lý video) là thành công.

HOÀN THÀNH: Gọi 'done' khi đã hoàn thành cả 2 Phase và đăng thành công ít nhất 10-15 nhóm.
    """


	attrs = ['aria-label', 'placeholder', 'role']

	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		controller=controller,
		available_file_paths=['/home/duongpv/Downloads/1.mp4', '/home/duongpv/Downloads/2.mp4'],
		use_vision=False,
		use_thinking=False,
		max_actions_per_step=3,
		include_attributes=attrs,
		max_failures=3,
		step_timeout=1200,
		llm_timeout=1200,
		max_history_items=6,
		extend_system_message='/no_think\nIMPORTANT: You MUST output ONLY valid JSON matching the schema. Do NOT include any reasoning, explanation, or text outside the JSON object.',
	)

	print('🔥 Bắt đầu chạy Agent...')
	try:
		await agent.run()
		print('✅ Đã hoàn thành tác vụ đăng video lên hội nhóm Facebook!')
	except Exception as e:
		print(f'❌ Có lỗi xảy ra trong quá trình chạy Agent: {e}')
	finally:
		await browser.close()


if __name__ == '__main__':
	asyncio.run(main())
