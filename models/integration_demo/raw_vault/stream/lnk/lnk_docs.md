## Tables
{% docs lnk_card_indi %}
Lưu trữ thông tin relationship giữa hub_card và hub_indi  
Bảng lnk_customer_account được load bởi apache spark structured stream  




{% enddocs %}

## Columns
{% docs dv_hkey_lnk_card_indi %}
hash key concat(CB_CIF_NO,CB_CUSTOMER_IDNO) được sinh ra bởi concat(CB_CIF_NO,CB_CUSTOMER_IDNO) bằng hàm SHA256
{% enddocs %}
