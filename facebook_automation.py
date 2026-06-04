import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, ChatGoogle

load_dotenv()

async def main():
	
	api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
	if not api_key:
		return None

	model_name = os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite')

	print(f'🚀 Đang khởi tạo LLM: {model_name}...')
	llm = ChatGoogle(model=model_name, api_key=api_key, temperature=0.0,thinking_budget=0)

	
	print("🌐 Đang khởi tạo Browser sử dụng Chrome Profile 'Default' (Dương Việt)...")
	browser = Browser(
		executable_path='/usr/bin/google-chrome', 
		user_data_dir='/home/duongpv/.config/google-chrome', 
		profile_directory='Default', 
		headless=False, 
	)

	task = """
    CÁC BƯỚC THỰC HIỆN TẦM QUAN TRỌNG CAO:
    1. Truy cập trang web https://www.facebook.com.
    2. Xác nhận đã đăng nhập tài khoản cá nhân (Dương Việt) nhờ Cookie/Session có sẵn từ profile Chrome.
    3. THỰC HIỆN CHUYỂN ĐỔI VAI TRÒ SANG PAGE "NGỌC KHUÊ STEM":
       - Nhấp vào ảnh đại diện cá nhân ở góc trên bên phải để mở menu tài khoản, sau đó chọn chuyển đổi sang vai trò Page "Ngọc Khuê Stem".
       - HOẶC: Truy cập trực tiếp đường dẫn Page của bạn tại https://www.facebook.com/NgocKhueStem (hoặc URL tương ứng của page). Tại đây, nếu thấy banner hoặc nút "Chuyển ngay" (Switch now) để chuyển sang tương tác dưới vai trò Page "Ngọc Khuê Stem", hãy click vào đó để chuyển đổi.
       - Đảm bảo rằng góc trên bên phải hiển thị ảnh đại diện và vai trò hoạt động hiện tại là Page "Ngọc Khuê Stem".
    4. SAU KHI ĐÃ CHUYỂN SANG VAI TRÒ PAGE: Tìm kiếm các hội nhóm (groups) trên Facebook liên quan đến các từ khóa: "stem" và "thuê đồ án". Tìm kiếm và lọc ra danh sách nhiều hội nhóm nhất có thể có số lượng thành viên nhiều nhất.
    5. Tiến hành đăng bài lên các nhóm này. Đối với mỗi nhóm:
       - Nhấp vào phần tạo bài viết ("Tạo bài viết công khai..." hoặc "Bạn đang nghĩ gì?").
       - Tìm và click vào nút tải lên Ảnh/Video (thường có biểu tượng ảnh/video hoặc nút "Ảnh/Video").
       - Tải lên cả hai video cùng một lúc bằng cách truyền một danh sách (list) chứa cả hai đường dẫn cục bộ vào tham số path của action upload_file: ["/home/duongpv/Downloads/1.mp4", "/home/duongpv/Downloads/2.mp4"]. TUYỆT ĐỐI không gọi upload_file hai lần riêng lẻ vì cuộc gọi thứ hai sẽ ghi đè lên file của cuộc gọi thứ nhất.
       - QUAN TRỌNG: Đợi cho đến khi các video được tải lên hoàn tất (thanh tiến trình biến mất, hiển thị bản xem trước của các video, và nút "Đăng" hoặc "Post" chuyển từ trạng thái bị vô hiệu hóa/màu xám sang trạng thái sẵn sàng hoạt động/màu xanh dương).
       - XỬ LÝ NÚT ĐĂNG (POST):
         + Nút "Đăng" (Post) thường là một thẻ div/button có `role="button"` và chứa chữ "Đăng" hoặc "Post" (hoặc có thuộc tính `aria-label="Đăng"` hoặc `aria-label="Post"`).
         + Hãy click vào phần tử này để đăng bài.
         + Nếu click bằng chuột bị lỗi hoặc không có phản hồi: Click vào ô soạn thảo nội dung (nơi nhập văn bản) để lấy tiêu điểm (focus), sau đó nhấn phím "Tab" liên tục vài lần để vùng chọn màu xanh chuyển đến nút "Đăng" (Post), rồi gửi phím "Enter" để đăng bài.
         + Chờ xác nhận bài viết đã đăng thành công trước khi chuyển sang nhóm tiếp theo. Lặp lại cho đến khi hoàn thành nhiều nhóm nhất có thể.
    """

	print('🧠 Đang tạo Agent thực hiện tác vụ...')
	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		available_file_paths=['/home/duongpv/Downloads/1.mp4', '/home/duongpv/Downloads/2.mp4'],
		use_vision=False,
        use_thinking=False,
		max_failures=5,
		step_timeout=300,
		llm_timeout=120,
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
