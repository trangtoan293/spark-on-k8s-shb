{%- macro ktlmdm_rule_template_config_yml() -%} 
{%- set yml -%}

name: ktlmdm
version: '1.0.0'


cleansing:
  - name: cleantp_remove_pattern
    rule_type: 'common'
    description: '- Cleansing rule : Remove special characters from the string'
    
  - name: cleantp_replace_head_phone
    rule_type: 'common'
    description: " 
      - Cleansing rule : Remove +84 or 84 and replace it with 0.
      - Update phone number prefixes according to Vietnamese carrier prefixes.
      - Uses reference table mdm_catalog_phone_number_prefix."

  - name: cleantp_replace_category
    rule_type: 'common'
    description: '
        - Cleansing rule : Replace values in a specified category field based on mapping rules.
        - Uses reference table mdm_catalog_category. '

  - name: cleantp_format_datetime
    rule_type: 'common'
    description: '- Cleansing rule : Format datetime fields according to standard or custom formats.'

validate:
  - name: validatetp_regex_not_like
    rule_type: 'common'
    description: '- Validate rule : Check if a string is valid according to a pattern structure.
                  - Params :
                    - regex_pattern : A custom pattern to validate the string value. If not provided, no pattern validation is applied.
                    - warning_null : Default is NO. It is used to indicate whether to validate errors for null values or not.
                 '
  
  - name: validatetp_format_CCCD_corr_YOB
    rule_type: 'special'
    description: '- Validate rule : Check the 5th and 6th digits in an ID card correspond to the year of birth.
                  - Params : 
                    - condition : Is a column the year of birth of the customer.
                    - warning_null : Default is NO. It is used to indicate whether to validate errors for null values or not.
                 '
  
  - name: validatetp_check_head_cccd
    rule_type: 'common'
    description: '- Validate rule : Check the first 3 digits in the CCCD match a valid province code in Vietnam.
                  - Uses reference table mdm_catalog_province_code.
                  - Params :
                    - catalog_condition : Default is MDM_CATALOG_PROVINCE_CODE. The name of the reference table .
                    - catalog_column : Default is PROVINCE_CODE. The name column using in the reference table being used. 
                    - warning_null : Default is NO. It is used to indicate whether to validate errors for null values or not.
                  '
  
  - name: validatetp_check_number_4_cccd
    rule_type: 'common'
    description: '- Validate rule : Check the 4 digits in the CCCD matches the customer gender.
                  - Uses reference table mdm_catalog_source_gender, mdm_catalog_personid_gender.
                  - Params : 
                    - catalog_condition : Default is [MDM_CATALOG_SOURCE_GENDER, MDM_CATALOG_PERSONID_GENDER]. The list name of the reference table.
                    - column_condition : Default is [KDI07:KDI05]. KDI07 column the year of birth of the customer AND KDI05 column the customer gender.
                  '
  
  - name: validatetp_check_invalid_email
    rule_type: 'common'
    description: '- Validate rule : Check email is valid. if email match the set of valid emails.
                  - Uses reference table mdm_catalog_invalid_email_address.
                  - Params : 
                    - catalog_condition : Default is MDM_CATALOG_INVALID_EMAIL_ADDRESS. The name of the reference table .
                    - catalog_column : Default is EMAIL. The name column using in the reference table being used.
                    - warning_null : Default is YES. It is used to indicate whether to validate errors for null values or not.
                 '
  
  - name: validatetp_check_invalid_email_domain
    rule_type: 'common'
    description: '- Validate rule : Check domain_email is valid. if domain_email match the set of valid domain_emails.
                  - Uses reference table mdm_catalog_invalid_email_domain.
                  - Params : 
                    - catalog_condition : Default is MDM_CATALOG_INVALID_EMAIL_DOMAIN. The name of the reference table .
                    - catalog_column : Default is DOMAIN_EMAIL. The name column using in the reference table being used.
                    - warning_null : Default is YES. It is used to indicate whether to validate errors for null values or not.
                 '
  
  - name: validatetp_check_invalid_category
    rule_type: 'common'
    description: '- Validate rule : Check if the value belongs to the system-defined category (e.g., occupation, gender, etc.). 
                  - Uses reference table mdm_catalog_category. 
                  - Params : 
                    - catalog_condition : Default is MDM_CATALOG_CATEGORY. The name of the reference table .
                    - column_condition : Default is [KDI05:gioi_tinh,KDI34_01:nghe_nghiep]. This key-value pair defines the corresponding column in the catalog for each category.
                    - warning_null : Default is YES. It is used to indicate whether to validate errors for null values or not.
                 '
                  
  - name: validatetp_check_length
    rule_type: 'common'
    description: '- Validate rule : Check if the string has a minimum length of number characters.
                  - Params : 
                    - column: Defines the number of characters to check.
                    - warning_null : Default is NO. It is used to indicate whether to validate errors for null values or not.
                 '

  - name: validatetp_check_format_sdt
    rule_type: 'common'
    description: '- Validate rule : Check if the phone number string matches the default value.
                  - Params :
                    - condition: Defautl is [0123456789:0000000000:0900000000:0100000000:0111222333:1111111111:9000000000:0999999999] list phone default.
                  '

  - name: validatetp_check_range_datetime
    rule_type: 'common'
    description: '- validate rule : 
                      -{1} Check if the default value of date fields is set to 1900-01-01.
                      -{2} Check if the customer age falls within the range of 0 to 120.
                      -{3} Check if any date fields have values greater than the current date.
                  
                  - Params:
                    - condition : Defines the condition for validation (e.g., specific field checks, date ranges, etc.)
                  '

  - name: validatetp_check_active_datetime_legal_id
    rule_type: 'common'
    description: '- Validate rule : Check the validity of the customers identification documents by verifying if the legal validity period of the documents is within the allowed range.
                  - Params:
                    - column_condition : Is a column the year of birth of the customer.
                    - condition : Default is [50:15]. This range is used to check the time validity of the document.
                  '

  - name: validatetp_check_legal_id
    rule_type: 'common' 
    description: '- Validate rule : Check if the nationality matches the type of identification document.
                  - Params:
                    - condition : Default is [KDI21_01:KDI22_01:KDI23_01]. This contains information about the customer identity document fields, such as ID card (CMND), Citizen ID (CCCD), and Passport.
                  '

  - name: validatetp_check_legal_id_range_datetime
    rule_type: 'common'
    description: '- Validate rule : Check customer ID validity if check validity between date of birth and ID issue date.
                  - Params:
                    - column_condition : Is a column the year of birth of the customer.
                  '

  - name: validatetp_check_null
    rule_type: 'common'
    description: '- Validate rule : Check for NULL(is null or "NULL" or "null") and space values.'


{%- endset -%} 
{%- set model = fromyaml(yml) -%} 
{{ return(model) }} 
{%- endmacro -%}
