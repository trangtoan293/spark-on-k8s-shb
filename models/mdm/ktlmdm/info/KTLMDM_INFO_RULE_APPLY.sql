{{
    config(
        pre_hook = [
            "DROP TABLE {{this}} purge",
        ]
    )
}}


SELECT A_TBL.*, D_TBL.description from {{ref("MDM_INFO_RULE_FIELD_APPLY")}} A_TBL
LEFT JOIN {{ref("MDM_RULE_DESC")}} D_TBL 
ON A_TBL.RULE_CODE = D_TBL.CODE