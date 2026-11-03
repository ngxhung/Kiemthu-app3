# test_login.py
# Tuần 5 - Bài kiểm thử chức năng Đăng nhập cho app Swag Labs
# 3 test case: đăng nhập thành công, sai username, sai password

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Tài khoản hợp lệ, theo đúng tài liệu timeline tuần 4
USERNAME_HOP_LE = "standard_user"
PASSWORD_HOP_LE = "secret_sauce"


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "emulator-5554"
    options.app = r"F:\App\Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"
    options.no_reset = True
    options.app_wait_activity = "com.swaglabsmobileapp.*"

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield drv
    drv.quit()


def dang_nhap(driver, username, password):
    """
    Hàm dùng chung cho cả 3 test: nhập username, nhập password, bấm LOGIN.
    Tách ra một hàm riêng để không phải lặp lại 3 lần.
    """
    o_username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Username"))
    )
    o_username.send_keys(username)

    o_password = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password")
    o_password.send_keys(password)

    nut_login = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN")
    nut_login.click()


def test_dang_nhap_thanh_cong(driver):
    """
    Test case 1:
    - Bước: nhập username và password đúng, bấm LOGIN
    - Kết quả mong đợi: vào được màn hình danh sách sản phẩm (Products)
    """
    dang_nhap(driver, USERNAME_HOP_LE, PASSWORD_HOP_LE)

    # Sau khi đăng nhập đúng, app chuyển sang màn Products.
    # Chờ tối đa 10 giây cho tới khi thấy chữ "PRODUCTS" xuất hiện.
    man_products = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
        )
    )
    assert man_products.is_displayed(), "Đăng nhập đúng nhưng không thấy màn hình Products"


def test_dang_nhap_sai_username(driver):
    """
    Test case 2:
    - Bước: nhập username sai, password đúng, bấm LOGIN
    - Kết quả mong đợi: hiện thông báo lỗi, không vào được app
    """
    dang_nhap(driver, "user_khong_ton_tai", PASSWORD_HOP_LE)

    # App Swag Labs hiện thông báo lỗi dạng text-Error-message khi đăng nhập sai.
    # Nếu chạy báo không tìm thấy phần tử này, mở Appium Inspector kiểm tra lại
    # accessibility id thật của khung thông báo lỗi rồi sửa dòng bên dưới.
    thong_bao_loi = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "test-Error message")
        )
    )
    assert thong_bao_loi.is_displayed(), "Đăng nhập sai username nhưng không thấy thông báo lỗi"


def test_dang_nhap_sai_password(driver):
    """
    Test case 3:
    - Bước: nhập username đúng, password sai, bấm LOGIN
    - Kết quả mong đợi: hiện thông báo lỗi, không vào được app
    """
    dang_nhap(driver, USERNAME_HOP_LE, "mat_khau_sai")

    thong_bao_loi = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "test-Error message")
        )
    )
    assert thong_bao_loi.is_displayed(), "Đăng nhập sai password nhưng không thấy thông báo lỗi"
