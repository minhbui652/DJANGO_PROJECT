# DJANGO_PROJECT
#### - Tạo dự án với django
#### - Tạo các model User, Product, Cart
#### - Kết nối với CSDL mysql workbench
#### - Tạo api CRUD bằng viewset cho User, Product, Cart
#### - Tạo api CRUD bằng api_view cho Product
#### - Tạo api đăng ký có mã hóa mật khẩu bằng django.contrib.auth.hashers
#### - Tạo api đăng nhập có cấp token bằng rest_framework_simplejwt
#### - Sử dụng drf_yasg để tạo swagger cho api
#### - Phân quyền người dùng theo user, group
#### - Tạo api CRUD bằng api_view cho Group, Permission
#### - Gửi mail với django.core.mail
#### - Sử dụng redis để cache dữ liệu lấy từ db, lưu otp ngắn hạn
#### - Sử dụng celery để gửi mail bất đồng bộ:
        pip install celery
        celery -A DemoDjango worker --loglevel=info --pool=solo
#### - Sử dụng thư viện Flower để theo dõi các task queue: 
        pip install flower
        celery -A DemoDjango flower
#### - Sử dụng Redis pub/sub cho luồng đăng ký người dùng, log được ghi vào file logs/user_signup.log
        - Gọi api register thành công, publish message 'register'
          subscribe nhận message và thực thi task generate_otp.
        - Gọi api verify_otp thành công, publish message 'verify_otp_success'
          subscribe nhận message và thực thi task activate_account, welcome_email.
        - Gọi api resend_otp thành công, publish message 'resend_otp'
          subscribe nhận message và thực thi task generate_otp.