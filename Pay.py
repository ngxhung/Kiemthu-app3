import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="function")
def driver():
    """Khởi tạo cấu hình Appium Session cho thiết bị Android"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"  # Thay đổi theo tên thiết bị thực tế
    options.app_package = "com.swaglabsmobileapp"
    options.app_activity = ".MainActivity"
    options.automation_name = "UiAutomator2"
    options.no_reset = True

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    driver.implicitly_wait(5)
    
    yield driver
    driver.quit()

def navigate_to_checkout_info(driver):
    """Hàm phụ trợ: Đăng nhập, thêm sản phẩm vào giỏ và đi đến màn hình Checkout Information"""
    try:
        # 1. Đăng nhập nếu chưa vào
        username_field = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-Username")
        if username_field:
            username_field[0].send_keys("standard_user")
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").send_keys("secret_sauce")
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()
            time.sleep(2)
        
        # 2. Thêm sản phẩm đầu tiên vào giỏ hàng
        add_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART")
        if add_btn:
            add_btn[0].click()
            
        # 3. Vào giỏ hàng
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Cart").click()
        time.sleep(1)
        
        # 4. Nhấn nút Checkout
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-CHECKOUT").click()
        time.sleep(1)
    except Exception as e:
        print(f"Lỗi khi điều hướng tới Checkout: {e}")

# Sử dụng pytest.mark.parametrize để kiểm thử với nhiều bộ dữ liệu khác nhau (Tuần 7 yêu cầu)
@pytest.mark.parametrize("first_name, last_name, postal_code", [
    ("Nguyen", "An", "100000"),
    ("Tran", "Binh", "700000"),
    ("Le", "Chi", "550000")
])
def test_checkout_information_with_waits(driver, first_name, last_name, postal_code):
    """Test case Tuần 7: Sử dụng Explicit Wait để nhập thông tin thanh toán"""
    navigate_to_checkout_info(driver)
    
    wait = WebDriverWait(driver, 10)
    
    # Sử dụng Explicit Wait (EC.visibility_of_element_located) để đảm bảo ô nhập liệu đã xuất hiện
    first_name_field = wait.until(
        EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-First Name"))
    )
    first_name_field.clear()
    first_name_field.send_keys(first_name)
    
    last_name_field = wait.until(
        EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Last Name"))
    )
    last_name_field.clear()
    last_name_field.send_keys(last_name)
    
    postal_code_field = wait.until(
        EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Zip/Postal Code"))
    )
    postal_code_field.clear()
    postal_code_field.send_keys(postal_code)
    
    # Ẩn bàn phím ảo trên Android nếu che nút Continue
    try:
        driver.hide_keyboard()
    except Exception:
        pass
    
    # Nhấn nút Continue
    continue_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "test-CONTINUE"))
    )
    continue_btn.click()
    
    # Kiểm tra đã chuyển thành công sang màn hình Checkout: Overview
    overview_title = wait.until(
        EC.visibility_of_element_located((AppiumBy.XPATH, "//*[@text='CHECKOUT: OVERVIEW']"))
    )
    assert overview_title.is_displayed(), "Chưa chuyển sang trang Tổng kết đơn hàng!"
    print(f"Thành công với dữ liệu: {first_name} {last_name}, Mã bưu điện: {postal_code}")