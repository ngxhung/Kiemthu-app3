# test_smoke.py
# Tuần 4 - Bài kiểm thử đầu tiên (smoke test) cho app Swag Labs
# Mục đích: mở app lên và kiểm tra có ô nhập tên đăng nhập hiện ra không.
# Nếu bài này chạy được nghĩa là: Appium server, driver UiAutomator2, máy ảo
# và app Swag Labs đều đã kết nối đúng với nhau.

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


@pytest.fixture
def driver():
    # "options" là nơi khai báo máy ảo nào, app nào sẽ được mở.
    # platformName/automationName: nói cho Appium biết dùng driver Android (UiAutomator2).
    # deviceName: tên máy ảo đã tạo ở Android Studio (xem trong Device Manager).
    # app: đường dẫn tới file .apk đã tải về (đổi lại đường dẫn thật trên máy bạn).
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"  # tên/ID máy ảo của bạn
    options.app = r"F:\App\Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"
    options.no_reset = True
    # App chạy rất nhanh qua SplashActivity, nên Appium phải chấp nhận
    # bất kỳ activity nào trong package (dấu *), không chỉ chờ đúng Splash,
    # nếu không sẽ lặp vô hạn kiểu "None of the expected package/activity..."
    options.app_wait_activity = "com.swaglabsmobileapp.*"

    # Kết nối tới Appium server đang chạy ở terminal riêng (http://127.0.0.1:4723)
    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield drv
    drv.quit()  # đóng app và dọn dẹp sau khi test xong, dù test pass hay fail


def test_man_hinh_dang_nhap_hien_o_username(driver):
    """
    Test case bằng lời:
    - Bước: mở app Swag Labs
    - Kết quả mong đợi: màn hình đăng nhập hiện ra, có ô nhập username
    """
    # Tìm phần tử bằng accessibility id - đây là cách ổn định nhất trên mobile
    # vì không phụ thuộc vào vị trí hay giao diện, chỉ phụ thuộc vào "nhãn"
    # mà lập trình viên app đã gắn cho ô đó.
    o_username = driver.find_element(
        by=AppiumBy.ACCESSIBILITY_ID, value="test-Username"
    )

    # assert: nếu điều kiện sai, pytest sẽ báo FAILED và in rõ dòng nào sai
    assert o_username.is_displayed(), "Không thấy ô nhập username trên màn hình đăng nhập" 