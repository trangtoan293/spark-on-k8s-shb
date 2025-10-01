# MDM Macro Error Fix Summary

## Error Description
When running `dbt run`, the following compilation error occurred:
```
Compilation Error in model KTLMDM_CRM_INDIVIDUAL_CLEANSING
'None' has no attribute 'get'

> in macro cleansing_registry_rule_replace_to_head_phone
> called by macro cleansing_find_rule
> called by macro cleansing_handle
```

## Root Cause Analysis [REH, IV]

### Primary Issue (Updated)
The error `'None' has no attribute 'get'` has **TWO root causes**:

1. **Missing Catalog Configuration** (Critical) - The variable `catalog_table` is not defined in `dbt_project.yml`
2. **Missing Null Validation** - Macros attempted to call `.get()` on `None` values without validation

### Code Flow
1. `KTLMDM_CRM_INDIVIDUAL_CLEANSING.sql` calls `cleansing_handle()`
2. `cleansing_handle()` calls `selected_info_rule_cleansing()` to get rule configuration
3. If `selected_info_rule_cleansing()` returns `None` (rule not found), it's passed to `cleansing_find_rule()`
4. `cleansing_find_rule()` routes to the appropriate registry macro (e.g., `cleansing_registry_rule_replace_to_head_phone`)
5. Registry macros attempted to access `rule_info.get('catalog_condition')` without null checking
6. **Result**: Compilation error when `rule_info` is `None`

## Files Modified

### 1. `/macros/mdm/main/cleansing/logic/cleansing_registry.sql`
Added null validation to all four registry macros:

#### Changes Made:
- **`cleansing_registry_rule_regex_pattern`** (lines 3-5)
  - Added null check for `rule_info` before accessing attributes
  - Raises descriptive error if `rule_info` is `None`

- **`cleansing_registry_rule_replace_to_head_phone`** (lines 26-28)
  - Added null check for `rule_info` before accessing `catalog_condition`
  - Raises descriptive error if `rule_info` is `None`

- **`cleansing_registry_rule_coalesce_catalog`** (lines 75-77)
  - Added null check for `rule_info` before accessing attributes
  - Raises descriptive error if `rule_info` is `None`

- **`cleansing_resigtry_rule_convert_str_to_data`** (lines 119-121)
  - Added null check for `rule_info` before accessing `from_str_format`
  - Raises descriptive error if `rule_info` is `None`

### 2. `/macros/mdm/main/cleansing/cleansing_handle.sql`
Added validation in the main handler macro:

#### Changes Made (lines 12-14):
- Added null check after calling `selected_info_rule_cleansing()`
- Raises descriptive error message indicating which rule was not found
- Provides guidance to check `rule_desc_config.yml`

### 3. `/macros/mdm/main/cleansing/common/cleansing_common.sql`
Improved safe attribute access:

#### Changes Made (lines 10-15):
- Changed from dictionary bracket notation `rule_info['key']` to `.get('key')`
- Prevents KeyError if rule configuration is missing expected attributes
- More defensive programming approach

### 4. `/macros/mdm/main/utils/ktl_mdm_utils_get_config.sql`
Added comprehensive validation for catalog configuration:

#### Changes Made (lines 26-44):
- Added null check for `var(name_type)` to detect missing configuration
- Added null check for `ref_group` within catalog configuration
- Improved error messages to show available catalog groups
- Provides clear guidance on what configuration is missing

## Benefits of These Changes [REH, IV, CA]

1. **Better Error Messages**: Instead of cryptic `'None' has no attribute 'get'`, users now see:
   ```
   MDMError: Rule 'CL2' not found in rule configuration. Please check your rule_desc_config.yml
   ```

2. **Early Failure Detection**: Errors are caught at the validation layer rather than deep in the execution stack

3. **Defensive Programming**: All macros now validate inputs before processing

4. **Maintainability**: Clear error messages make debugging easier for future developers

## Testing Recommendations

1. **Test with valid configuration**: Run `dbt run` to ensure the fixes don't break existing functionality
2. **Test with missing rule**: Temporarily remove a rule from `ktlmdm_rule_desc.sql` to verify error handling
3. **Test with incomplete rule**: Remove a required attribute (e.g., `catalog_condition`) to verify safe attribute access

## Configuration Verification

The following rules are configured for CRM INDIVIDUAL cleansing:
- **CL1**: Remove special characters (pattern: `[-/., ]`)
- **CL2**: Replace phone number prefixes (catalog: `integration_demo.MDM_PHONE_NUMBER_PREFIX`)
- **CL3**: Standardize category codes (catalog: `integration_demo.mdm_catalog_category`)

All required attributes are present in the configuration files.

## Next Steps - CRITICAL CONFIGURATION REQUIRED

### 1. Add Catalog Configuration to `dbt_project.yml`
**This is required before running dbt again!**

See `CATALOG_CONFIG_REQUIRED.md` for detailed instructions.

Add this to your `dbt_project.yml`:
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

### 2. Verify Catalog Tables Exist
- `integration_demo.MDM_PHONE_NUMBER_PREFIX`
- `integration_demo.mdm_catalog_category`

### 3. Run dbt
```bash
dbt run --select KTLMDM_CRM_INDIVIDUAL_CLEANSING
```

### 4. If Errors Persist
- Verify column names match your actual catalog table schemas
- Check source view `VW_KTLMDM_CRM_INDIVIDUAL_INGEST` exists
- Review error messages for specific missing configurations

## Applied Rules
[REH] - Robust Error Handling
[IV] - Input Validation  
[CA] - Clean Architecture
[SF] - Simplicity First
[RP] - Readability Priority
