{%- macro ktlmdm_rule_field_apply_config_yml() -%} 
{%- set yml -%}

name: ktlmdm
version: '1.0.0'

KTL_MDM:
  - product: INDIVIDUAL
    source_system:
      - name: COREBANK
        cleansing:
          - name: CL1
            list_column:
              - KDI5
              - KDI05
              - KDI17
              - KDI21_01
              - KDI22_01
              - KDI58_01
              - KDI23_01

          - name: CL2
            list_column:
              - KDI17

          - name: CL3
            list_column: 
              - KDI5
            
              
        validate:
          - name: V1
            list_column: 
              - KDI17
          - name: V4
            list_column: 
              - KDI17
          - name: V2
            list_column: 
              - KDI19
          - name: G1
            list_column: 
              - KDI19
              - KDI15
          - name: V8
            list_column: 
              - KDI22_01
          - name: S267
            list_column: 
              - KDI21_02
          - name: S35
            list_column: 
              - KDI21_02
          - name: S132
            list_column: 
              - KDI2
          - name: S234
            list_column: 
              - KDI7
          - name: S261
            list_column: 
              - KDI7

        match:
          auto_match_pkkey_priority_by:
            TOTAL_ERR_CNT: ASC
            KDI52: ASC

          matched_by_rules:
            - name: M1
              type: manual
              straight:
                match_column_1: KDI2
                match_column_2: KDI22_01

            - name: M2
              type: manual
              straight:
                match_column_1: KDI2
                match_column_2: KDI21_01

            - name: M3
              type: manual
              straight:
                match_column_1: KDI2
                match_column_2: KDI23_01

            - name: M4
              type: manual
              straight:
                match_column_1: KDI22_01

            - name: M5
              type: manual
              straight:
                match_column_1: KDI21_01

            - name: M6
              type: manual
              straight:
                match_column_1: KDI23_01              

            - name: M7
              type: manual
              cross:
                  match_group_1: [KDI23_01,KDI22_01,KDI21_01]

      - name: CORECARD
        cleansing:
          - name: CL1
            list_column:
              - KDI5
              - KDI05
              - KDI17
              - KDI21_01
              - KDI22_01
              - KDI58_01
              - KDI23_01

          - name: CL2
            list_column:
              - KDI17

          - name: CL3
            list_column: 
              - KDI5
              
              
        validate:
          - name: V1
            list_column: 
              - KDI17
          - name: V2
            list_column: 
              - KDI19
          - name: G1
            list_column: 
              - KDI19
              - KDI15
          - name: V8
            list_column: 
              - KDI22_01
          - name: S267
            list_column: 
              - KDI21_02
          - name: S35
            list_column: 
              - KDI21_02
          - name: S132
            list_column: 
              - KDI2
          - name: S234
            list_column: 
              - KDI7
          - name: S261
            list_column: 
              - KDI7

        match:
          auto_match_pkkey_priority_by:
            TOTAL_ERR_CNT: ASC
            KDI52: ASC

          matched_by_rules:
            - name: M1
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI22_01

            - name: M2
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI21_01

            - name: M3
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI23_01

            - name: M4
              type: manual
              straight:
                match_column_1: KDI22_01

            - name: M5
              type: manual
              straight:
                match_column_1: KDI21_01

            - name: M6
              type: manual
              straight:
                match_column_1: KDI23_01              

            - name: M7
              type: manual
              cross:
                  match_group_1: [KDI23_01,KDI22_01,KDI21_01]


      - name: CRM
        cleansing:
          - name: CL1
            list_column:
              - KDI5
              - KDI05
              - KDI17
              - KDI21_01
              - KDI22_01
              - KDI58_01
              - KDI23_01

          - name: CL2
            list_column:
              - KDI17

          - name: CL3
            list_column: 
              - KDI5
          
              
        validate:
          - name: V1
            list_column: 
              - KDI17
          - name: V2
            list_column: 
              - KDI19
          - name: G1
            list_column: 
              - KDI19
              - KDI15
          - name: V8
            list_column: 
              - KDI22_01
          - name: S267
            list_column: 
              - KDI21_02
          - name: S35
            list_column: 
              - KDI21_02
          - name: S132
            list_column: 
              - KDI2
          - name: S234
            list_column: 
              - KDI7
          - name: S261
            list_column: 
              - KDI7

        match:
          auto_match_pkkey_priority_by:
            TOTAL_ERR_CNT: ASC
            KDI52: ASC

          matched_by_rules:
            - name: M1
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI22_01

            - name: M2
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI21_01

            - name: M3
              type: auto
              straight:
                match_column_1: KDI2
                match_column_2: KDI23_01

            - name: M4
              type: manual
              straight:
                match_column_1: KDI22_01

            - name: M5
              type: manual
              straight:
                match_column_1: KDI21_01

            - name: M6
              type: manual
              straight:
                match_column_1: KDI23_01              

            - name: M7
              type: manual
              cross:
                  match_group_1: [KDI23_01,KDI22_01,KDI21_01]

      
      - name: MDM
        merge:
          - name: MR1

  - product: CORP
    source_system:
      - name: COREBANK
        cleansing:
          - name: CL1
            list_column:
              - KDC28
          - name: CL2
            list_column:
              - KDC28
          - name: CL5
            list_column:
              - KDC05_02
              - KDC16_02

        validate:
          - name: V1
            list_column: 
              - KDC28
          - name: V2
            list_column: 
              - KDC09

          - name: G1
            list_column: 
              - KDC02
              - KDC09
              - KDC28

          - name: S132
            list_column: 
              - KDC02

        match:
          auto_match_pkkey_priority_by:
            TOTAL_ERR_CNT: ASC

          matched_by_rules:
            - name: M1
              type: auto
              straight:
                match_column_1: KDC02
                match_column_2: KDC05_01

            - name: M2
              type: manual
              straight:
                match_column_1: KDC05_01


      - name: CORECARD
        cleansing:
          - name: CL1
            list_column:
              - KDC05_02
              - KDC16_01
              - KDC16_02
              - KDC28
              - KDC31

          - name: CL2
            list_column:
                - KDC28

        validate:
          - name: V1
            list_column: 
              - KDC28
          - name: V2
            list_column: 
              - KDC09

          - name: G1
            list_column: 
              - KDC02
              - KDC10
              - KDC28

          - name: S132
            list_column: 
              - KDC02

        match:
          auto_match_pkkey_priority_by:
            TOTAL_ERR_CNT: ASC
            
          matched_by_rules:
            - name: M1
              type: auto
              straight:
                match_column_1: KDC02
                match_column_2: KDC05_01

            - name: M2
              type: manual
              straight:
                match_column_1: KDC05_01


{%- endset -%} 
{%- set model = fromyaml(yml) -%} 
{{ return(model) }} 
{%- endmacro -%}
