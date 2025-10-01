# Missing Catalog Configuration

## Root Cause
The error `'None' has no attribute 'get'` is caused by **missing catalog configuration** in `dbt_project.yml`.

The macro `ktl_mdm_get_info_table_catalog()` expects a variable called `catalog_table` to be defined, but it's not present in your configuration.

## Required Configuration

Add the following to your `dbt_project.yml` file under the `vars:` section:

```yaml
vars:
  catalog_table:
    ref_group:
      - name: mdm_phone_number_prefix
        table: integration_demo.MDM_PHONE_NUMBER_PREFIX
        column_old_phone: old_phone
        column_new_phone: new_phone
      
      - name: mdm_catalog_category
        table: integration_demo.mdm_catalog_category
        column_original_value: original_value
        column_standard_value: standard_value
        column_category_type: category_type
        column_source: source
```

## Explanation

### Phone Number Prefix Catalog
- **name**: `mdm_phone_number_prefix` - Referenced in CL2 rule
- **table**: The actual table name containing phone prefix mappings
- **column_old_phone**: Column containing old phone prefixes (e.g., "090", "091")
- **column_new_phone**: Column containing new phone prefixes (e.g., "032", "033")

### Category Catalog
- **name**: `mdm_catalog_category` - Referenced in CL3 rule
- **table**: The actual table name containing category mappings
- **column_original_value**: Column with original category values from source systems
- **column_standard_value**: Column with standardized category values
- **column_category_type**: Column indicating category type (e.g., 'gioi_tinh', 'nghe_nghiep')
- **column_source**: Column indicating source system (e.g., 'COREBANK', 'CRM')

## Complete dbt_project.yml Example

```yaml
name: 'simple_dbt_project'
version: '1.0.0'
config-version: 2
profile: 'simple_dbt_project'

model-paths: ["models"]
test-paths: ["tests"]
target-path: "/tmp/dbt_target"
log-path: "/tmp/dbt_logs"
clean-targets: ["/tmp/dbt_target", "/tmp/dbt_logs"]

vars:
  catalog_table:
    ref_group:
      - name: mdm_phone_number_prefix
        table: integration_demo.MDM_PHONE_NUMBER_PREFIX
        column_old_phone: old_phone
        column_new_phone: new_phone
      
      - name: mdm_catalog_category
        table: integration_demo.mdm_catalog_category
        column_original_value: original_value
        column_standard_value: standard_value
        column_category_type: category_type
        column_source: source

models:
  simple_dbt_project:
    staging:
      +materialized: view
      +file_format: iceberg
    marts:
      +materialized: table
      +file_format: iceberg
```

## Action Required

1. **Update `dbt_project.yml`** with the catalog configuration above
2. **Verify table names** - Ensure the catalog tables exist:
   - `integration_demo.MDM_PHONE_NUMBER_PREFIX`
   - `integration_demo.mdm_catalog_category`
3. **Verify column names** - Adjust column names to match your actual catalog table schemas
4. **Run dbt again**: `dbt run --select KTLMDM_CRM_INDIVIDUAL_CLEANSING`

## Additional Catalogs

If you use other validation rules (V9, V18, R43, R57, etc.), you may need to add more catalog groups:

```yaml
      - name: mdm_catalog_province_code
        table: integration_demo.mdm_catalog_province_code
        column_province_code: province_code
      
      - name: mdm_catalog_zerobound_email
        table: integration_demo.mdm_catalog_zerobound_email
        column_email: email
        column_email_domain: email_domain
```

## Applied Rules
[IV] - Input Validation
[REH] - Robust Error Handling
[SD] - Strategic Documentation
