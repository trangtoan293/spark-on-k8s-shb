# Autovault Macros - Documentation

**Data Vault 2.0 Automation for dbt-spark (Batch Processing)**

---

## 📋 Overview

Autovault provides YAML-driven macros to automatically generate Data Vault 2.0 tables:
- **Hubs** - Business entities with hash keys
- **Satellites** - Descriptive attributes with change tracking  
- **Links** - Relationships between hubs
- **Link-Satellites** - Relationship attributes

### Key Features:
✅ YAML configuration (no SQL needed)  
✅ SHA-256 hash key generation  
✅ Multi-source support with collision codes  
✅ CDC (Change Data Capture) aware  
✅ Batch/incremental materialization  
✅ Automatic deduplication  

---

## 🏗️ Architecture (After Refactor)

```
macros/autovault/
├── core/                    # Foundation layer
│   ├── constants.sql        # Hard-coded values (separators, null values)
│   ├── validation.sql       # YAML config validation
│   └── helpers.sql          # Shared utilities
├── hash/                    # Hash generation (DO NOT MODIFY)
│   ├── normalize.sql        # Column normalization logic
│   └── generate_key.sql     # SHA-256 hash key generation
├── hub/                     # Hub transformation
│   ├── hub_transform.sql    # Main Hub macro
│   └── hub_helpers.sql      # Hub-specific helpers
└── utils/                   # Legacy (backward compatibility)
    └── derive_columns.sql   # Old implementation
```

---

## 🚀 Quick Start

### 1. Create YAML Configuration

```yaml
# ktl_autovault_configs/hub/hub_customer.yml
target_schema: raw_vault
target_table: hub_customer
target_entity_type: hub
collision_code: CORE
source_schema: source
source_table: corebank_customer

columns:
  # Hash Key - generated from business keys
  - key_type: hash_key_hub
    source: [CUSTOMER_ID]  # Can be composite: [ID1, ID2]
    target: dv_hkey_hub_customer
    dtype: string
  
  # Business Key - actual data
  - key_type: biz_key
    source:
      name: CUSTOMER_ID
      dtype: int
    target: CUSTOMER_ID
    dtype: int
```

### 2. Create dbt Model

```sql
-- models/raw_vault/hub_customer.sql
{{ hub_transform(
    model=fromyaml(var('hub_customer_config')),
    dv_system=var('dv_system')
) }}
```

### 3. Configure dbt_project.yml

```yaml
vars:
  dv_system:
    columns:
      - target: dv_kaf_ldt
        dtype: timestamp
        description: 'Kafka load timestamp'
        source:
          name: ktime
          dtype: timestamp
      
      - target: dv_src_ldt
        dtype: timestamp
        description: 'Source system timestamp'
        source:
          name: optime
          dtype: timestamp
      
      - target: dv_cdc_ops
        dtype: string
        description: 'CDC operation (I/U/D)'
        source:
          name: cdc_operation
          dtype: string
      
      - target: dv_ccd
        dtype: string
        description: 'Collision code'
        source:
          name: collision_code
          dtype: string
```

### 4. Run Model

```bash
# Full refresh
dbt run --select hub_customer --full-refresh

# Incremental
dbt run --select hub_customer
```

---

## 📖 Detailed Usage

### Hub Configuration

```yaml
target_schema: <schema_name>        # Required
target_table: <table_name>          # Required
target_entity_type: hub             # Required - must be 'hub'
collision_code: <SOURCE_CODE>       # Required - e.g. 'CORE', 'CARD', 'CRM'
source_schema: <source_schema>      # Optional - default: 'source'
source_table: <source_table_name>   # Required

columns:
  # REQUIRED: At least one hash_key_hub
  - key_type: hash_key_hub
    source: [COL1, COL2]           # List for composite keys
    target: dv_hkey_hub_<entity>
    dtype: string
  
  # REQUIRED: At least one biz_key
  - key_type: biz_key
    source:
      name: <source_column>
      dtype: <source_dtype>
    target: <target_column>
    dtype: <target_dtype>
```

### Multi-Source Hub Example

```yaml
# Hub for Customer (multiple sources)
target_schema: raw_vault
target_table: hub_customer
target_entity_type: hub

# Source 1: Core Banking
sources:
  - source_table: corebank_customer
    collision_code: CORE
    columns:
      - key_type: hash_key_hub
        source: [CUSTOMER_ID]
        target: dv_hkey_hub_customer
      - key_type: biz_key
        source: {name: CUSTOMER_ID, dtype: int}
        target: CUSTOMER_ID
        
  - source_table: card_customer
    collision_code: CARD
    columns:
      - key_type: hash_key_hub
        source: [CB_CUS_ID]
        target: dv_hkey_hub_customer
      - key_type: biz_key
        source: {name: CB_CUS_ID, dtype: int}
        target: CUSTOMER_ID  # Mapped to same column
```

---

## 🔑 Hash Key Generation

### How It Works

```sql
-- Input columns: CUSTOMER_ID = 12345, SOURCE = 'CORE'
-- Process:
1. Normalize: coalesce(nullif(rtrim(upper(cast(12345 as string))), ''), '-1')
   Result: '12345'

2. Concatenate with separator: '12345' || '||' || 'CORE'

3. Hash: sha2('12345||CORE', 256)
   Result: 'a3f2b1c...' (64-character hex)
```

### Important Rules

⚠️ **DO NOT MODIFY hash generation logic** - it affects existing data!

- Separator: `||` (hard-coded in `constants.sql`)
- Null replacement: `-1` (hard-coded)
- Algorithm: SHA-256 (256 bits)
- Business keys: Always UPPERCASE
- Composite keys: Joined with `||` separator
- Collision code: Appended at end

---

## 🔄 Deduplication Logic

Hubs keep only **ONE** record per hash key (the earliest):

```sql
-- Window function orders by load timestamps
ROW_NUMBER() OVER (
    PARTITION BY dv_hkey_hub_customer
    ORDER BY dv_kaf_ldt ASC, dv_src_ldt ASC
) AS row_num

-- Keep first appearance only
WHERE row_num = 1
```

**Data Vault Rule:** First appearance wins!

---

## 🧪 Testing

### Validate Hash Generation

```sql
-- Compare old vs new implementation
WITH test_data AS (
    SELECT 'ABC123' AS customer_id, 'CORE' AS source
),

old_hash AS (
    SELECT {{ _render_hash_key_transformation(...) }} AS hash_key
    FROM test_data
),

new_hash AS (
    SELECT {{ generate_hash_key_hub(...) }} AS hash_key
    FROM test_data
)

SELECT * FROM old_hash
EXCEPT
SELECT * FROM new_hash;
-- Should return 0 rows
```

### Validate Hub Output

```bash
# Check row counts
dbt run --select hub_customer --full-refresh
# Count should match deduplicated source records

# Check for duplicates
SELECT hash_key, COUNT(*) 
FROM raw_vault.hub_customer
GROUP BY hash_key
HAVING COUNT(*) > 1;
-- Should return 0 rows
```

---

## 📊 Performance Tips

### 1. Partitioning

```yaml
# models/hub_customer.sql
{{ config(
    partition_by=['load_date'],
    cluster_by=['dv_hkey_hub_customer']
) }}

{{ hub_transform(...) }}
```

### 2. Incremental Strategy

```yaml
# dbt_project.yml
models:
  raw_vault:
    +materialized: incremental
    +incremental_strategy: append  # For Spark
    +file_format: iceberg
```

### 3. Source Filtering

Add WHERE clause in source for large tables:

```yaml
# In YAML config (future feature)
source_filter: "load_date >= '2024-01-01'"
```

---

## 🐛 Troubleshooting

### Error: "Hub config validation failed: Missing 'collision_code'"

**Cause:** YAML config incomplete  
**Solution:** Add `collision_code` field to YAML

### Error: "Hash key is null"

**Cause:** Business key columns contain nulls  
**Solution:** Check source data quality, ensure business keys are not null

### Error: "Undefined macro 'generate_hash_key_hub'"

**Cause:** Missing hash generation macros  
**Solution:** Ensure `macros/autovault/hash/generate_key.sql` exists

### Hash Keys Don't Match After Refactor

**Cause:** Logic modification or config change  
**Solution:** 
1. Compare old vs new hash with test query
2. Check separator and null values in `constants.sql`
3. Verify column order and collision code

---

## 🔧 Maintenance

### Adding New Hash Algorithm

```sql
-- macros/autovault/core/constants.sql
{%- macro dv_hash_algorithm() -%}
    {{ return({'function': 'sha2', 'bits': 512}) }}  # Change to SHA-512
{%- endmacro -%}
```

⚠️ This will break existing hash keys! Use with caution.

### Custom Collision Code Column

```sql
-- macros/autovault/core/constants.sql
{%- macro dv_collision_code_column() -%}
    {{ return('source_system_code') }}  # Custom name
{%- endmacro -%}
```

---

## 📚 Additional Resources

- **Data Vault 2.0 Spec:** https://datavaultalliance.com/
- **dbt Documentation:** https://docs.getdbt.com/
- **Internal Docs:** See `REFACTOR_EXECUTION_PLAN.md`

---

## ✅ Migration Checklist (Old → New)

If migrating from old autovault implementation:

- [ ] Backup existing models
- [ ] Test hash generation matches exactly
- [ ] Update model calls to remove `materialized` parameter
- [ ] Remove streaming-specific configs
- [ ] Run full-refresh on dev environment
- [ ] Compare row counts and hash keys
- [ ] Update CI/CD pipelines
- [ ] Document changes for team

---

**Last Updated:** 2025-09-30  
**Version:** 2.0 (Refactored - Batch Only)
