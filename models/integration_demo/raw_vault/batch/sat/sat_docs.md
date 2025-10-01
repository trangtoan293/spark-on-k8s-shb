## Tables
{% docs sat_card_indi %}
Lưu trữ thông tin mô tả của khách hàng cá nhân hệ thống thẻ 
Bảng sat_card_indi được load bởi apache spark structured stream  
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất  

```render_dv_erd_docs(hub_indi,sat_card_indi)```

{% enddocs %}

{% docs sat_core_indi %}
Lưu trữ thông tin mô tả của khách hàng cá nhân hệ thống core
Bảng sat_core_indi được load bởi apache spark structured stream  
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất  

```render_dv_erd_docs(hub_indi,sat_core_indi)```
{% enddocs %}

{% docs sat_crm_indi %}
Lưu trữ thông tin mô tả của khách hàng cá nhân hệ thống crm
Bảng sat_crm_indi được load bởi apache spark structured stream  
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất  

```render_dv_erd_docs(hub_indi,sat_crm_indi)```

{% enddocs %}

{% docs sat_snp_card_indi %}
Lưu trữ thông tin mô tả gần nhất của khách hàng cá nhân hệ thống thẻ 
Bảng sat_snp_card_indi được load bởi apache spark structured stream   

```render_dv_erd_docs(hub_indi,sat_card_indi)```

{% enddocs %}

{% docs sat_snp_core_indi %}
Lưu trữ thông tin mô tả của khách hàng cá nhân hệ thống core
Bảng sat_snp_core_indi được load bởi apache spark structured stream  

```render_dv_erd_docs(hub_indi,sat_core_indi)```

{% enddocs %}

{% docs sat_snp_crm_indi %}
Lưu trữ thông tin mô tả của khách hàng cá nhân hệ thống crm
Bảng sat_snp_core_indi được load bởi apache spark structured stream  

```render_dv_erd_docs(hub_indi,sat_crm_indi)```

{% enddocs %}

{% docs sat_card_corp %}
Lưu trữ thông tin mô tả của khách hàng doanh nghiệp hệ thống thẻ 
Bảng sat_card_corp được load bởi apache spark structured stream  
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất  

```render_dv_erd_docs(hub_corp,sat_card_corp)```

{% enddocs %}

{% docs sat_core_corp %}
Lưu trữ thông tin mô tả của khách hàng doanh nghiệp hệ thống core
Bảng sat_core_corp được load bởi apache spark structured stream  
Dữ liệu được lưu trữ trong vòng 7 ngày gần nhất  

```render_dv_erd_docs(hub_corp,sat_core_corp)```
{% enddocs %}

{% docs sat_snp_card_corp %}
Lưu trữ thông tin mô tả gần nhất của khách hàng doanh nghiệp hệ thống thẻ 
Bảng sat_snp_card_corp được load bởi apache spark structured stream   

```render_dv_erd_docs(hub_corp,sat_card_corp)```

{% enddocs %}

{% docs sat_snp_core_corp %}
Lưu trữ thông tin mô tả của khách hàng doanh nghiệp hệ thống core
Bảng sat_snp_core_corp được load bởi apache spark structured stream  

```render_dv_erd_docs(hub_corp,sat_core_corp)```

{% enddocs %}

## Columns
{% docs dv_hkey_sat_card_indi %}
hash key CB_CUS_ID được sinh ra bởi CB_CUS_ID bằng hàm SHA256
{% enddocs %}

{% docs dv_hkey_sat_core_indi %}
hash key CUS_CUSTOMER_CODE được sinh ra bởi CUS_CUSTOMER_CODE bằng hàm SHA256
{% enddocs %}

{% docs dv_hkey_sat_crm_indi %}
hash key CRM_CUS_ID được sinh ra bởi CRM_CUS_ID bằng hàm SHA256
{% enddocs %}

{% docs dv_hkey_sat_card_corp %}
hash key CB_CUSTOMER_CODE được sinh ra bởi CB_CUSTOMER_CODE bằng hàm SHA256
{% enddocs %}

{% docs dv_hkey_sat_core_corp %}
hash key CUS_CUSTOMER_CODE được sinh ra bởi CUS_CUSTOMER_CODE bằng hàm SHA256
{% enddocs %}