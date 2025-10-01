## Tables
{% docs lsat_der_customer_account %}
Lưu trữ thông tin mô tả của bảng lnk_customer_account
Bảng lsat_der_customer_account được load bởi apache spark structured stream
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất
{% enddocs %}

## Columns

{% docs dv_hkey_lsat_customer_account %}
unique hash key của account id + customer id + dv_src_ldt + dv_kaf_ldt + dv_kaf_ofs, được sinh ra bằng hàm SHA256
{% enddocs %}
