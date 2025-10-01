## Tables
{% docs hub_indi %}
Thông tin id của khách hàng cá nhân được lưu trữ tập trung tại bảng hub_indi
Bảng hub_indi được load bởi apache spark structured stream  



{% enddocs %}

{% docs hub_corp %}
Thông tin id của khách hàng doanh nghiệp được lưu trữ tập trung tại bảng hub_corp
Bảng hub_corp được load bởi apache spark structured stream  



{% enddocs %}

## Columns

{% docs dv_hkey_hub_indi %}
Hash key CUS_CUSTOMER_CODE được sinh ra bởi CUS_CUSTOMER_CODE bằng hàm SHA256
{% enddocs %}

{% docs dv_hkey_hub_corp %}
Hash key CUS_CUSTOMER_CODE được sinh ra bởi CUS_CUSTOMER_CODE bằng hàm SHA256
{% enddocs %}

