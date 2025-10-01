{%- macro ktlmdm_metadata_config_yml() -%} 
{%- set yml -%}

name: ktlmdm
version: '1.0.0'

KTL_MDM:
  - product: INDIVIDUAL
    source_system:
      - name: COREBANK
        columns:
          - name: mdm_ldt
            data_type: TIMESTAMP(6)
            is_ldt: true

          - name: cob_date
            data_type: DATE
            is_cob_date: true

          - name: BRN_CODE
            data_type: VARCHAR2(255)
            is_master_key: true

          - name: KDI1
            data_type: VARCHAR2(255)
            description: 'Mã khách hàng cá nhân tại source nguồn'
            is_pk: true

          - name: KDI2
            data_type: VARCHAR2(255)
            description: 'Họ và tên khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI3
            data_type: VARCHAR2(255)
            description: 'Danh xưng khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI4
            data_type: VARCHAR2(255)
            description: 'Biệt danh của khách hàng (tên gọi khác)'
            is_master_key: true
            has_cdt: true

          - name: KDI5
            data_type: VARCHAR2(255)
            description: 'Giới tính'
            is_master_key: true
            has_cdt: true

          - name: KDI6
            data_type: VARCHAR2(255)
            description: 'Dân tộc'
            is_master_key: true
            has_cdt: true

          - name: KDI7
            data_type: DATE
            description: 'Ngày sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI8
            data_type: VARCHAR2(255)
            description: 'Thông tin cư trú/ không cư trú'
            is_master_key: true
            has_cdt: true

          - name: KDI9
            data_type: VARCHAR2(255)
            description: 'Trình độ học vấn'
            is_master_key: true
            has_cdt: true

          - name: KDI10
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI10_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI10_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI10_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI10_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI10_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI10_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI11
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng'
            is_master_key: true
            has_cdt: true

          - name: KDI11_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI11_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI11_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI11_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI11_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI11_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI12
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ'
            is_master_key: true
            has_cdt: true

          - name: KDI12_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI12_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI12_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI12_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI12_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI12_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI13
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú'
            is_master_key: true
            has_cdt: true

          - name: KDI13_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI13_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI13_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI13_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI13_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI13_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI14
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú'
            is_master_key: true
            has_cdt: true

          - name: KDI14_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI14_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI14_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI14_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI14_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI14_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI15
            data_type: VARCHAR2(255)
            description: 'Quốc tịch'
            is_master_key: true
            has_cdt: true

          - name: KDI16
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhà (số máy bàn)'
            is_master_key: true
            has_cdt: true

          - name: KDI17
            data_type: VARCHAR2(255)
            description: 'Số điện thoại di động'
            is_master_key: true
            has_cdt: true

          - name: KDI18
            data_type: VARCHAR2(255)
            description: 'Số điện thoại cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI19
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI20
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI21_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_02
            data_type: DATE
            description: 'Ngày cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_01
            data_type: VARCHAR2(255)
            description: 'Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_02
            data_type: DATE
            description: 'Ngày cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI23_01
            data_type: VARCHAR2(255)
            description: 'Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_02
            data_type: DATE
            description: 'Ngày cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI24_01
            data_type: VARCHAR2(255)
            description: 'Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI25_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI26_01
            data_type: VARCHAR2(255)
            description: 'Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI27_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI28_01
            data_type: VARCHAR2(255)
            description: 'Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI29_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI30_01
            data_type: VARCHAR2(255)
            description: 'Thị thực (đối với người nước ngoài ở VN)'
            is_master_key: true
            has_cdt: true

          - name: KDI30_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_04
            data_type: VARCHAR2(255)
            description: 'Thời hạn TT (có giá trị đến ngày)'
            is_master_key: true
            has_cdt: true

          - name: KDI31
            data_type: VARCHAR2(255)
            description: 'Số thẻ xanh'
            is_master_key: true
            has_cdt: true

          - name: KDI32
            data_type: VARCHAR2(255)
            description: 'Địa chỉ gửi nhờ thư tại Hoa Kỳ'
            is_master_key: true
            has_cdt: true

          - name: KDI33_01
            data_type: VARCHAR2(255)
            description: 'Mã số thuế cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI33_02
            data_type: VARCHAR2(255)
            description: 'Nơi cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_03
            data_type: VARCHAR2(255)
            description: 'Ngày cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực mã số thuế'
            is_master_key: true
            has_cdt: true

          - name: KDI34_01
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp I'
            is_master_key: true
            has_cdt: true

          - name: KDI34_02
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp II'
            is_master_key: true
            has_cdt: true

          - name: KDI34_03
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp III'
            is_master_key: true
            has_cdt: true

          - name: KDI34_04
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp IV'
            is_master_key: true
            has_cdt: true

          - name: KDI34_05
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp V'
            is_master_key: true
            has_cdt: true

          - name: KDI35
            data_type: VARCHAR2(255)
            description: 'Tình trạng sở hữu nhà cửa'
            is_master_key: true
            has_cdt: true

          - name: KDI36
            data_type: VARCHAR2(255)
            description: 'Số người phụ thuộc'
            is_master_key: true
            has_cdt: true

          - name: KDI37
            data_type: VARCHAR2(255)
            description: 'Tình trạng hôn nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI38
            data_type: VARCHAR2(255)
            description: 'Mã người hôn phối (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI39
            data_type: VARCHAR2(255)
            description: 'Tên vợ/chồng'
            is_master_key: true
            has_cdt: true

          - name: KDI40
            data_type: VARCHAR2(255)
            description: 'Chức danh hiện tại của khách hàng tại nơi làm việc'
            is_master_key: true
            has_cdt: true

          - name: KDI41
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận thông báo số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI42
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mật khẩu Online'
            is_master_key: true
            has_cdt: true

          - name: KDI43
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận OTP'
            is_master_key: true
            has_cdt: true

          - name: KDI44
            data_type: VARCHAR2(255)
            description: 'Số DTDĐ đăng ký thông báo biến động số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI45
            data_type: VARCHAR2(255)
            description: 'Lý lịch tư pháp'
            is_master_key: true
            has_cdt: true

          - name: KDI46
            data_type: VARCHAR2(255)
            description: 'Mã người giám hộ/ người đại diện pháp luật (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI47
            data_type: VARCHAR2(255)
            description: 'Tên người giám hộ/ người đại diện pháp luật'
            is_master_key: true
            has_cdt: true

          - name: KDI48
            data_type: VARCHAR2(255)
            description: 'Nguồn thu nhập chính'
            is_master_key: true
            has_cdt: true

          - name: KDI49
            data_type: VARCHAR2(255)
            description: 'Thu nhập của hộ gia đình/tháng'
            is_master_key: true
            has_cdt: true

          - name: KDI50
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận mật khẩu KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI51
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mã kích hoạt Safe key KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI52
            data_type: DATE
            description: 'Ngày mở pers'
            is_master_key: true
            has_cdt: true

          - name: KDI53
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản vay (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI54
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản tiền gửi (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI55
            data_type: VARCHAR2(255)
            description: 'Mã CIF khách hàng cá nhân COREBANK'
            is_master_key: true
            has_cdt: true


      - name: CORECARD
        columns:
          - name: mdm_ldt
            data_type: TIMESTAMP(6)
            is_ldt: true

          - name: cob_date
            data_type: DATE
            is_cob_date: true

          - name: BRN_CODE
            data_type: VARCHAR2(255)
            is_master_key: true

          - name: KDI1
            data_type: VARCHAR2(255)
            description: 'Mã khách hàng cá nhân tại source nguồn'
            is_pk: true

          - name: KDI2
            data_type: VARCHAR2(255)
            description: 'Họ và tên khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI3
            data_type: VARCHAR2(255)
            description: 'Danh xưng khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI4
            data_type: VARCHAR2(255)
            description: 'Biệt danh của khách hàng (tên gọi khác)'
            is_master_key: true
            has_cdt: true

          - name: KDI5
            data_type: VARCHAR2(255)
            description: 'Giới tính'
            is_master_key: true
            has_cdt: true

          - name: KDI6
            data_type: VARCHAR2(255)
            description: 'Dân tộc'
            is_master_key: true
            has_cdt: true

          - name: KDI7
            data_type: DATE
            description: 'Ngày sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI8
            data_type: VARCHAR2(255)
            description: 'Thông tin cư trú/ không cư trú'
            is_master_key: true
            has_cdt: true

          - name: KDI9
            data_type: VARCHAR2(255)
            description: 'Trình độ học vấn'
            is_master_key: true
            has_cdt: true

          - name: KDI10
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI10_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI10_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI10_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI10_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI10_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI10_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI11
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng'
            is_master_key: true
            has_cdt: true

          - name: KDI11_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI11_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI11_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI11_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI11_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI11_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI12
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ'
            is_master_key: true
            has_cdt: true

          - name: KDI12_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI12_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI12_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI12_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI12_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI12_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI13
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú'
            is_master_key: true
            has_cdt: true

          - name: KDI13_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI13_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI13_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI13_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI13_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI13_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI14
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú'
            is_master_key: true
            has_cdt: true

          - name: KDI14_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI14_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI14_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI14_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI14_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI14_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI15
            data_type: VARCHAR2(255)
            description: 'Quốc tịch'
            is_master_key: true
            has_cdt: true

          - name: KDI16
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhà (số máy bàn)'
            is_master_key: true
            has_cdt: true

          - name: KDI17
            data_type: VARCHAR2(255)
            description: 'Số điện thoại di động'
            is_master_key: true
            has_cdt: true

          - name: KDI18
            data_type: VARCHAR2(255)
            description: 'Số điện thoại cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI19
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI20
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI21_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_02
            data_type: DATE
            description: 'Ngày cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_01
            data_type: VARCHAR2(255)
            description: 'Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_02
            data_type: DATE
            description: 'Ngày cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI23_01
            data_type: VARCHAR2(255)
            description: 'Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_02
            data_type: DATE
            description: 'Ngày cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI24_01
            data_type: VARCHAR2(255)
            description: 'Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI25_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI26_01
            data_type: VARCHAR2(255)
            description: 'Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI27_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI28_01
            data_type: VARCHAR2(255)
            description: 'Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI29_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI30_01
            data_type: VARCHAR2(255)
            description: 'Thị thực (đối với người nước ngoài ở VN)'
            is_master_key: true
            has_cdt: true

          - name: KDI30_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_04
            data_type: VARCHAR2(255)
            description: 'Thời hạn TT (có giá trị đến ngày)'
            is_master_key: true
            has_cdt: true

          - name: KDI31
            data_type: VARCHAR2(255)
            description: 'Số thẻ xanh'
            is_master_key: true
            has_cdt: true

          - name: KDI32
            data_type: VARCHAR2(255)
            description: 'Địa chỉ gửi nhờ thư tại Hoa Kỳ'
            is_master_key: true
            has_cdt: true

          - name: KDI33_01
            data_type: VARCHAR2(255)
            description: 'Mã số thuế cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI33_02
            data_type: VARCHAR2(255)
            description: 'Nơi cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_03
            data_type: VARCHAR2(255)
            description: 'Ngày cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực mã số thuế'
            is_master_key: true
            has_cdt: true

          - name: KDI34_01
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp I'
            is_master_key: true
            has_cdt: true

          - name: KDI34_02
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp II'
            is_master_key: true
            has_cdt: true

          - name: KDI34_03
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp III'
            is_master_key: true
            has_cdt: true

          - name: KDI34_04
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp IV'
            is_master_key: true
            has_cdt: true

          - name: KDI34_05
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp V'
            is_master_key: true
            has_cdt: true

          - name: KDI35
            data_type: VARCHAR2(255)
            description: 'Tình trạng sở hữu nhà cửa'
            is_master_key: true
            has_cdt: true

          - name: KDI36
            data_type: VARCHAR2(255)
            description: 'Số người phụ thuộc'
            is_master_key: true
            has_cdt: true

          - name: KDI37
            data_type: VARCHAR2(255)
            description: 'Tình trạng hôn nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI38
            data_type: VARCHAR2(255)
            description: 'Mã người hôn phối (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI39
            data_type: VARCHAR2(255)
            description: 'Tên vợ/chồng'
            is_master_key: true
            has_cdt: true

          - name: KDI40
            data_type: VARCHAR2(255)
            description: 'Chức danh hiện tại của khách hàng tại nơi làm việc'
            is_master_key: true
            has_cdt: true

          - name: KDI41
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận thông báo số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI42
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mật khẩu Online'
            is_master_key: true
            has_cdt: true

          - name: KDI43
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận OTP'
            is_master_key: true
            has_cdt: true

          - name: KDI44
            data_type: VARCHAR2(255)
            description: 'Số DTDĐ đăng ký thông báo biến động số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI45
            data_type: VARCHAR2(255)
            description: 'Lý lịch tư pháp'
            is_master_key: true
            has_cdt: true

          - name: KDI46
            data_type: VARCHAR2(255)
            description: 'Mã người giám hộ/ người đại diện pháp luật (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI47
            data_type: VARCHAR2(255)
            description: 'Tên người giám hộ/ người đại diện pháp luật'
            is_master_key: true
            has_cdt: true

          - name: KDI48
            data_type: VARCHAR2(255)
            description: 'Nguồn thu nhập chính'
            is_master_key: true
            has_cdt: true

          - name: KDI49
            data_type: VARCHAR2(255)
            description: 'Thu nhập của hộ gia đình/tháng'
            is_master_key: true
            has_cdt: true

          - name: KDI50
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận mật khẩu KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI51
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mã kích hoạt Safe key KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI52
            data_type: DATE
            description: 'Ngày mở pers'
            is_master_key: true
            has_cdt: true

          - name: KDI53
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản vay (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI54
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản tiền gửi (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI55
            data_type: VARCHAR2(255)
            description: 'Mã CIF khách hàng cá nhân COREBANK'
            is_master_key: true
            has_cdt: true


      - name: CRM
        columns:
          - name: mdm_ldt
            data_type: TIMESTAMP(6)
            is_ldt: true

          - name: cob_date
            data_type: DATE
            is_cob_date: true

          - name: BRN_CODE
            data_type: VARCHAR2(255)
            is_master_key: true
            
          - name: KDI1
            data_type: VARCHAR2(255)
            description: 'Mã khách hàng cá nhân tại source nguồn'
            is_pk: true

          - name: KDI2
            data_type: VARCHAR2(255)
            description: 'Họ và tên khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI3
            data_type: VARCHAR2(255)
            description: 'Danh xưng khách hàng cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI4
            data_type: VARCHAR2(255)
            description: 'Biệt danh của khách hàng (tên gọi khác)'
            is_master_key: true
            has_cdt: true

          - name: KDI5
            data_type: VARCHAR2(255)
            description: 'Giới tính'
            is_master_key: true
            has_cdt: true

          - name: KDI6
            data_type: VARCHAR2(255)
            description: 'Dân tộc'
            is_master_key: true
            has_cdt: true

          - name: KDI7
            data_type: DATE
            description: 'Ngày sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI8
            data_type: VARCHAR2(255)
            description: 'Thông tin cư trú/ không cư trú'
            is_master_key: true
            has_cdt: true

          - name: KDI9
            data_type: VARCHAR2(255)
            description: 'Trình độ học vấn'
            is_master_key: true
            has_cdt: true

          - name: KDI10
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI10_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI10_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI10_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI10_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI10_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI10_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ cơ quan_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI11
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng'
            is_master_key: true
            has_cdt: true

          - name: KDI11_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI11_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI11_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI11_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI11_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI11_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ nhà riêng_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI12
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ'
            is_master_key: true
            has_cdt: true

          - name: KDI12_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI12_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI12_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI12_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI12_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI12_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ liên hệ_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI13
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú'
            is_master_key: true
            has_cdt: true

          - name: KDI13_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI13_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI13_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI13_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI13_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI13_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ tạm trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI14
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú'
            is_master_key: true
            has_cdt: true

          - name: KDI14_01
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quốc gia'
            is_master_key: true
            has_cdt: true

          - name: KDI14_02
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Tỉnh/thành phố trực thuộc trương ương'
            is_master_key: true
            has_cdt: true

          - name: KDI14_03
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Quận/Huyện'
            is_master_key: true
            has_cdt: true

          - name: KDI14_04
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Phường/Xã'
            is_master_key: true
            has_cdt: true

          - name: KDI14_05
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Đường'
            is_master_key: true
            has_cdt: true

          - name: KDI14_06
            data_type: VARCHAR2(255)
            description: 'Địa chỉ thường trú_Số nhà'
            is_master_key: true
            has_cdt: true

          - name: KDI15
            data_type: VARCHAR2(255)
            description: 'Quốc tịch'
            is_master_key: true
            has_cdt: true

          - name: KDI16
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhà (số máy bàn)'
            is_master_key: true
            has_cdt: true

          - name: KDI17
            data_type: VARCHAR2(255)
            description: 'Số điện thoại di động'
            is_master_key: true
            has_cdt: true

          - name: KDI18
            data_type: VARCHAR2(255)
            description: 'Số điện thoại cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI19
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI20
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email cơ quan'
            is_master_key: true
            has_cdt: true

          - name: KDI21_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_02
            data_type: DATE
            description: 'Ngày cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI21_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh nhân dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_01
            data_type: VARCHAR2(255)
            description: 'Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_02
            data_type: DATE
            description: 'Ngày cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI22_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Căn cước công dân'
            is_master_key: true
            has_cdt: true

          - name: KDI23_01
            data_type: VARCHAR2(255)
            description: 'Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_02
            data_type: DATE
            description: 'Ngày cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI23_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực Passport'
            is_master_key: true
            has_cdt: true

          - name: KDI24_01
            data_type: VARCHAR2(255)
            description: 'Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI24_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy khai sinh'
            is_master_key: true
            has_cdt: true

          - name: KDI25_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI25_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép lái xe'
            is_master_key: true
            has_cdt: true

          - name: KDI26_01
            data_type: VARCHAR2(255)
            description: 'Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI26_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Thẻ bảo hiểm y tế'
            is_master_key: true
            has_cdt: true

          - name: KDI27_01
            data_type: VARCHAR2(255)
            description: 'Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI27_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Giấy phép hành nghề'
            is_master_key: true
            has_cdt: true

          - name: KDI28_01
            data_type: VARCHAR2(255)
            description: 'Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI28_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Sổ hộ khẩu'
            is_master_key: true
            has_cdt: true

          - name: KDI29_01
            data_type: VARCHAR2(255)
            description: 'Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI29_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp Chứng minh thư bộ đội'
            is_master_key: true
            has_cdt: true

          - name: KDI30_01
            data_type: VARCHAR2(255)
            description: 'Thị thực (đối với người nước ngoài ở VN)'
            is_master_key: true
            has_cdt: true

          - name: KDI30_02
            data_type: VARCHAR2(255)
            description: 'Ngày cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_03
            data_type: VARCHAR2(255)
            description: 'Nơi cấp TT'
            is_master_key: true
            has_cdt: true

          - name: KDI30_04
            data_type: VARCHAR2(255)
            description: 'Thời hạn TT (có giá trị đến ngày)'
            is_master_key: true
            has_cdt: true

          - name: KDI31
            data_type: VARCHAR2(255)
            description: 'Số thẻ xanh'
            is_master_key: true
            has_cdt: true

          - name: KDI32
            data_type: VARCHAR2(255)
            description: 'Địa chỉ gửi nhờ thư tại Hoa Kỳ'
            is_master_key: true
            has_cdt: true

          - name: KDI33_01
            data_type: VARCHAR2(255)
            description: 'Mã số thuế cá nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI33_02
            data_type: VARCHAR2(255)
            description: 'Nơi cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_03
            data_type: VARCHAR2(255)
            description: 'Ngày cấp MST'
            is_master_key: true
            has_cdt: true

          - name: KDI33_04
            data_type: VARCHAR2(255)
            description: 'Ngày hết hiệu lực mã số thuế'
            is_master_key: true
            has_cdt: true

          - name: KDI34_01
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp I'
            is_master_key: true
            has_cdt: true

          - name: KDI34_02
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp II'
            is_master_key: true
            has_cdt: true

          - name: KDI34_03
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp III'
            is_master_key: true
            has_cdt: true

          - name: KDI34_04
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp IV'
            is_master_key: true
            has_cdt: true

          - name: KDI34_05
            data_type: VARCHAR2(255)
            description: 'Nghề nghiệp_Mã Cấp V'
            is_master_key: true
            has_cdt: true

          - name: KDI35
            data_type: VARCHAR2(255)
            description: 'Tình trạng sở hữu nhà cửa'
            is_master_key: true
            has_cdt: true

          - name: KDI36
            data_type: VARCHAR2(255)
            description: 'Số người phụ thuộc'
            is_master_key: true
            has_cdt: true

          - name: KDI37
            data_type: VARCHAR2(255)
            description: 'Tình trạng hôn nhân'
            is_master_key: true
            has_cdt: true

          - name: KDI38
            data_type: VARCHAR2(255)
            description: 'Mã người hôn phối (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI39
            data_type: VARCHAR2(255)
            description: 'Tên vợ/chồng'
            is_master_key: true
            has_cdt: true

          - name: KDI40
            data_type: VARCHAR2(255)
            description: 'Chức danh hiện tại của khách hàng tại nơi làm việc'
            is_master_key: true
            has_cdt: true

          - name: KDI41
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận thông báo số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI42
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mật khẩu Online'
            is_master_key: true
            has_cdt: true

          - name: KDI43
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận OTP'
            is_master_key: true
            has_cdt: true

          - name: KDI44
            data_type: VARCHAR2(255)
            description: 'Số DTDĐ đăng ký thông báo biến động số dư'
            is_master_key: true
            has_cdt: true

          - name: KDI45
            data_type: VARCHAR2(255)
            description: 'Lý lịch tư pháp'
            is_master_key: true
            has_cdt: true

          - name: KDI46
            data_type: VARCHAR2(255)
            description: 'Mã người giám hộ/ người đại diện pháp luật (nếu có)'
            is_master_key: true
            has_cdt: true

          - name: KDI47
            data_type: VARCHAR2(255)
            description: 'Tên người giám hộ/ người đại diện pháp luật'
            is_master_key: true
            has_cdt: true

          - name: KDI48
            data_type: VARCHAR2(255)
            description: 'Nguồn thu nhập chính'
            is_master_key: true
            has_cdt: true

          - name: KDI49
            data_type: VARCHAR2(255)
            description: 'Thu nhập của hộ gia đình/tháng'
            is_master_key: true
            has_cdt: true

          - name: KDI50
            data_type: VARCHAR2(255)
            description: 'Địa chỉ email nhận mật khẩu KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI51
            data_type: VARCHAR2(255)
            description: 'Số điện thoại nhận mã kích hoạt Safe key KHCN'
            is_master_key: true
            has_cdt: true

          - name: KDI52
            data_type: DATE
            description: 'Ngày mở pers'
            is_master_key: true
            has_cdt: true

          - name: KDI53
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản vay (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI54
            data_type: VARCHAR2(255)
            description: 'KH hiện có khoản tiền gửi (Y/N)'
            is_master_key: true
            has_cdt: true

          - name: KDI55
            data_type: VARCHAR2(255)
            description: 'Mã CIF khách hàng cá nhân COREBANK'
            is_master_key: true
            has_cdt: true


  - product: CORP
    source_system:
      - name: COREBANK
        columns:
          - name: mdm_ldt
            data_type: TIMESTAMP(6)
            is_ldt: true

          - name: cob_date
            data_type: DATE
            is_cob_date: true
          
          - name: BRN_CODE
            data_type: VARCHAR2(255)
            is_master_key: true
          
          - name: KDC01
            date_type: bigint
            description: ''
            is_pk: true
          
          - name: KDC02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC04
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC05_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC05_02
            date_type: date
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC05_03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC06
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC07
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC08
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC09
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC10
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11_03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11_04
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC11_05
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC12
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC13
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC14_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC14_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC14_03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC14_04
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC14_05
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC15_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC15_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC15_03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC15_04
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC15_05
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC16_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC16_02
            date_type: date
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC16_03
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC17
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC18
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC19
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC20
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC21
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC22_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC22_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC23_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC23_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC24_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC24_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC25_01
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC25_02
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC26
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC27
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC28
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC29
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC30
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC31
            date_type: date
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC32
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC33
            date_type: string
            description: ''
            is_pk: false
            is_master_key: true
          
          - name: KDC34
            date_type: bigint
            description: ''
            is_pk: false
            is_master_key: true


      - name: CORECARD
        columns:
          - name: mdm_ldt
            data_type: TIMESTAMP(6)
            is_ldt: true

          - name: cob_date
            data_type: DATE
            is_cob_date: true
          
          - name: BRN_CODE
            data_type: VARCHAR2(255)
            is_master_key: true
            
          - name: KDC01
            data_type: bigint
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC04
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC05_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC05_02
            data_type: date
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC05_03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC06
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC07
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC08
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC09
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC10
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11_03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11_04
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC11_05
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC12
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC13
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC14_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC14_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC14_03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC14_04
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC14_05
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC15_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC15_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC15_03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC15_04
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC15_05
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC16_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC16_02
            data_type: timestamp
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC16_03
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC17
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC18
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC19
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC20
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC21
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC22_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC22_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC23_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC23_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC24_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC24_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC25_01
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC25_02
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC26
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC27
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC28
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC29
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC30
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC31
            data_type: date
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC32
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC33
            data_type: string
            description: ''
            is_pk: false
            is_master_key: true

          - name: KDC34
            data_type: bigint
            description: ''
            is_pk: false
            is_master_key: true
  




{%- endset -%} 
{%- set model = fromyaml(yml) -%} 
{{ return(model) }} 
{%- endmacro -%}