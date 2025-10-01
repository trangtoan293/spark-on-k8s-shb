{%- macro ktlmdm_rule_desc_config_yml() -%} 
{%- set yml -%}

name: ktlmdm
version: '1.0.0'

cleansing:
  - code: CL1
    description: 'Xóa ký tự trong chuỗi: khoảng trắng, dấu chấm, dấu phẩy, dấu "- / \"'
    rule_template: cleantp_remove_pattern
    character: '[-/., ]'
    
  - code: CL2
    description: 'Thay thế ký tự trong chuỗi: xử lý "+84", chuyển đổi đầu số của các nhà mạng Việt Nam'
    rule_template: cleantp_replace_head_phone
    catalog_condition: integration_demo.MDM_PHONE_NUMBER_PREFIX

  - code: CL3
    description: 'Chuẩn hóa danh mục: chuẩn hóa bộ mã danh mục thống nhất giữa các hệ thống CoreBanking, CoreCard, LOS, CRM, ....'
    rule_template: cleantp_replace_category
    catalog_condition: integration_demo.mdm_catalog_category
    column_condition: 'KDI5:gioi_tinh,KDI34_01:nghe_nghiep'
  
  - code: CL4
    description: 'Xóa ký tự sau chuỗi "-%"'
    rule_template: cleantp_remove_character_hypen
  
  - code: CL5
    description: 'Format date: chuyển đổi kiểu dữ liệu kiểu chuỗi sang kiểu date'
    rule_template: cleantp_format_datetime
    from_str_format: 'yyyyMMdd'

  - code: CL6
    description: 'Xóa tất cả các ký tự khoảng trắng'
    rule_template: cleantp_remove_space
    

validate:
  - code: V1
    description: 'Tất cả số trong SĐT DD phải là số từ 0 - 9, không chứa ký tự đặc biệt'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[0-9]+$'
    warning_null: NO

  - code: V2
    description: 'Kiểm tra cấu trúc địa chỉ email (4 thành phần, quy định từng thành phần)'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    warning_null: NO

  - code: V3
    description: 'Cấu trúc MST (10 ký tự số hoặc 10 ký tự số + "-" + 3 ký tự số'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^\d{10}(-\d{3})?$'
    warning_null: NO

  - code: V4
    description: 'Kiểm tra SĐT DD: 10 ký tự số'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^\d{10}$'
    warning_null: NO

  - code: V5
    description: 'Cấu trúc CMND: 9 hoặc 12 ký tự số'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^(\d{9}|\d{12})$'
    warning_null: NO

  - code: V6
    description: 'Cấu trúc PP: bao gồm 7 hoặc 8 hoặc 9 ký tự bao gồm ký tự đầu là chữ và các ký tự sau là số'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[A-Za-z][A-Za-z0-9]{6,8}$'
    warning_null: NO

  - code: V7
    description: 'Kiểm tra cấu trúc CCCD: 12 ký tự số'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^\d{12}$'
    warning_null: NO

  - code: V8
    description: 'Cấu trúc CCCD: 2 số cuối trong năm sinh phải phù hợp với chữ số thứ 5 và 6 trong CCCD'
    rule_template: validatetp_format_CCCD_corr_YOB
    condition: 'KDI7'
    warning_null: NO

  - code: V9
    description: 'Cấu trúc CCCD: 3 số đầu phải thuộc bảng mã số thẻ CCCD các tỉnh thành'
    rule_template: check_head_cccd
    catalog_condition: integration_demo.mdm_catalog_province_code
    catalog_column: province_code
    warning_null: NO

  - code: V10
    description: 'Cấu trúc CCCD: số thứ 4 phải phù hợp với giới tính'
    rule_template: validatetp_check_number_4_cccd
    catalog_condition: [integration_demo.mdm_catalog_source_gender, integration_demo.mdm_catalog_personid_gender]
    column_condition: 'KDI7:KDI5'

  - code: R57
    description: 'Kiểm tra thông tin Email hợp lệ (có xử lý multi): thuộc tập email valid (zerobound)'
    rule_template: validatetp_check_invalid_email
    catalog_condition: integration_demo.mdm_catalog_zerobound_email
    catalog_column: email
    warning_null: YES

  - code: R57_M
    description: ''
    rule_template: check_invalid_email_multi
    catalog_condition: integration_demo.mdm_catalog_zerobound_email
    catalog_column: email
    warning_null: YES

  - code: V30
    description: ''
    rule_template: check_invalid_email_domain
    catalog_condition: integration_demo.mdm_catalog_zerobound_email
    catalog_column: email_domain

  - code: V30_M
    description: ''
    rule_template: check_invalid_email_domain_multi
    catalog_condition: integration_demo.mdm_catalog_zerobound_email
    catalog_column: email_domain

  - code: R43
    description: 'Kiểm tra giá trị thuộc danh mục hệ thống (danh mục nghề nghiệp, giới tính, …)'
    rule_template: check_invalid_category
    catalog_condition: integration_demo.mdm_catalog_category
    warning_null: YES
    column_condition: 'KDI5:gioi_tinh,KDI34_01:nghe_nghiep'

  - code: V16
    description: 'kiểm tra thông tin: Quốc tịch phù hợp với Loại giấy tờ tùy thân'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[[:alpha:]]+([[:space:]][[:alpha:]]+)*$'
    warning_null: NO

  - code: V18
    description: 'Kiểm tra SĐT DD: 3 chữ số đầu phải thuộc danh sách các nhà mạng Việt Nam'
    rule_template: check_head_cccd
    catalog_condition: integration_demo.mdm_phone_number_prefix
    catalog_column: new_phone
    warning_null: NO

  - code: S123
    description: 'Kiểm tra chuỗi có độ dài tối thiểu: 4 ký tự'
    rule_template: check_length
    condition: '4'
    warning_null: NO

  - code: S134
    description: 'Kiểm tra chuỗi có độ dài tối thiểu: 3 ký tự'
    rule_template: check_length
    condition: '3'
    warning_null: NO

  - code: S132
    description: 'Kiểm tra chuỗi có độ dài tối thiểu: 2 ký tự'
    rule_template: check_length
    condition: '2'
    warning_null: NO

  - code: S224
    description: 'Kiểm tra chuỗi có giá trị mặc định 0123456789, 0000000000, 090000000000, 010000000000, 0111222333, 1111111111, 900000000000'
    rule_template: check_format_sdt
    condition: '0123456789:0000000000:0900000000:0100000000:0111222333:1111111111:9000000000:0999999999'

  - code: S261
    description: 'Kiểm tra giá trị mặc đinh của các trường kiểu date: 1900-01-01'
    rule_template: check_range_datetime
    condition: '1900-01-01'
    warning_null: NO

  - code: S267
    description: 'Kiểm tra hiệu lực giấy tờ tùy thân của khách hàng: kiểm tra khoảng pháp lý giấy tờ của khách hàng'
    rule_template: check_active_datetime_legal_id
    column_condition: 'KDI7'
    condition: '50:15'

  - code: R51
    description: 'Kiểm tra Quốc tịch có phù hợp với loại giấy tờ tùy thân'
    rule_template: check_legal_id
    condition: 'KDI21_01:KDI22_01:KDI23_01'

  - code: S31
    description: 'Kiểm tra các trường kiểu ngày vi phạm giá trị lớn hơn ngày hiện tại'
    rule_template: check_range_datetime

  - code: S234
    description: 'Kiểm tra tuổi của khách hàng có thuộc dải 0-120'
    rule_template: check_range_datetime
    condition: '0:120'

  - code: S35
    description: 'Kiểm tra hiệu lực giấy tờ tùy thân của khách hàng: kiểm tra khoảng hợp lệ giữa ngày sinh và ngày cấp giấy tờ tùy thân'
    rule_template: check_legal_id_range_datetime
    column_condition: 'KDI7'

  - code: G1
    description: 'Kiểm tra giá trị NULL(is null or "NULL" or "null") và space'
    rule_template: check_null

  - code: G3
    description: 'Check giá trị mặc định 0'
    rule_template: check_value_cannot_0
    regex_pattern: '^0$'
    warning_null: NO

  - code: V88
    description: ''
    rule_template: check_cccd_multi_value
    condition: 'KDI7'

  - code: S124
    description: 'Kiểm tra cấu trúc SĐT quốc tế'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^[0 00 +]([1-9]{1}|[0-9])'
    warning_null: NO

  - code: S125
    description: 'Kiểm tra cấu trúc SĐT'
    rule_template: validatetp_regex_not_like
    regex_pattern: '^(0|84|\+84)(3|5|7|8|9)\d{8}$'
    warning_null: NO

  - code: S36
    description: 'Kiểm tra cấu trúc email hợp lệ'
    rule_template: validatetp_regex_not_like
    regex_pattern: ^[a-zA-Z0-9]*[a-zA-Z0-9.''\`\%\&\_\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,4}$
    warning_null: NO

  - code: S229
    description: 'Kiểm tra email thuộc tập giá trị mặc định'
    rule_template: check_prefix_suffix_email
    catalog_condition: [integration_demo.MDM_CATALOG_PREFIX_EMAIL, integration_demo.MDM_CATALOG_SUFFIX_EMAIL]
    condition: 'PRE_EMAIL:SUFFIX_EMAIL'

  - code: G34
    description: 'Kiểm tra Họ tên KHCN hoặc Tên tỉnh thành'
    rule_template: regex_not_like_G34
    regex_pattern: ^[A-Za-z]([A-Za-z''.,| \-]|[''.,| \-](?![''.,| \-]))*[A-Za-z]$
    warning_null: YES

  - code: G36
    description: 'Kiểm tra chuỗi có ký tự chữ, ký tự số, ký tự đặc biệt (không được đứng đầu hoặc cuối chuỗi)'
    rule_template: regex_not_like_G36
    regex_pattern_1: ^[A-Za-z0-9].*[A-Za-z0-9]$
    regex_pattern_2: ([A-Za-z0-9''&(),.+:| /\-])
    warning_null: YES 

{%- endset -%} 
{%- set model = fromyaml(yml) -%} 
{{ return(model) }} 
{%- endmacro -%}