import streamlit as st
import pandas as pd
import re
import time

def header_animation() -> None:
    _animation_header = f'''
    .ani_head {{
    	position:relative;
    	overflow:hidden;
    	box-shadow:0 4px 20px rgba(0, 0, 0, 0.2);
    	margin:0 auto;
    	width:300px;
    	height:30px;
    	background-color:#f0f8ff;
        margin: 0 calc(50% - 50vw);
        width: 100vw;
    }}
    .ani_head::before,
    .ani_head::after {{
    	position:absolute;
    	left:-50%;
    	width:200%;
    	height:200%;
    	content:"";
    	background-color:#1e90ff;
    	animation:wave linear 6s infinite;
    }}
    .ani_head::before {{
    	top:-150%;
    	border-radius:50% 50% / 50% 70%;
    }}
    .ani_head::after {{
    	top:-146%;
    	border-radius:30% 70% / 30% 50%;
    	opacity:0.2;
    	animation-delay:0.4s;
    }}
    @keyframes wave {{
    	from {{
    		transform:rotate(0deg);
    	}}
    	to {{
    		transform:rotate(360deg);
    	}}
    }}
    '''
    st.markdown(
        f'''<div class="ani_head"></div><style>{_animation_header}</style>''', 
        unsafe_allow_html=True
    )

def explaining_part( _showed_table: object) -> None:

    _quetion_hover = f'''
    .qhover {{
      background-color: rgb(190, 205, 214);
      padding: 30px;
    }}
    .qhover .box {{
      border-radius: 10px;
    }}
    .qhover {{
      background-color: rgb(240, 240, 250);
      transition: box-shadow 0.5s;
      color: #696969;
      box-shadow:
        10px 10px 30px transparent,
        -10px -10px 30px transparent,
        inset 10px 10px 30px rgba(18, 47, 61, 0.5),
        inset -10px -10px 30px rgba(248, 253, 255, 0.9);

    }}
    .qhover:hover {{
      color: #a0522d;
      box-shadow:
        10px 10px 30px rgba(18, 47, 61, 0.5),
        -10px -10px 30px rgba(248, 253, 255, 0.9),
        inset 10px 10px 30px transparent,
        inset -10px -10px 30px transparent;
    }}
    '''
    st.markdown(
        f'''<p><div class="qhover">
        雪の結晶株式会社は、自社提供のサービスの一般利用者の情報をデータベースに保存しています.<br>
        所属部門/権限(Role)によって、閲覧できるユーザ情報は厳しく制限されています.<br>
        <br>
        あなたはデータエンジニアであり、部署に割り当てられた権限（Role）に成り代わることにより、他部署所属の社員が「どのデータを閲覧できるか/どのデータを閲覧できないか」を確認することができます.<br>
        <br>
        さて、どの部署所属であれば<br>
        「サービスの本会員」かつ「データ利用の許諾済み」の一般利用者の人数を確認することができるでしょうか？
        </div><style>{_quetion_hover}</style></p>''', 
        unsafe_allow_html=True
    )
    st.divider()

    with st.expander('選択肢：あなたが利用できるネットワーク（開く）'):
        st.markdown('''
        - インターネット
        - 社内ネットワークA（IPレンジ：203.0.113.0/26)
        - 社内ネットワークB（IPレンジ：203.0.113.64/26）
        - 社内ネットワークC（IPレンジ：203.0.113.128/26）
        - 社内ネットワークD（IPレンジ：198.51.100.0/24)
        '''
        )

    with st.expander('選択肢：存在する部署毎のRole（開く）'):
        st.markdown('''
        - セキュリティ部所属の社員は Role「:red[SECURITY_DEPT_ROLE]」 を利用できます.
        - 総務部所属の社員は Role「:orange[GENERAL_AFFAIRS_DEPT_ROLE]」を利用できます.
        - 購買部所属の社員は Role「:green[PURCHASING_DEPT_ROLE]」を利用できます.
        - 経営企画部所属の社員は Role「:blue[CORPORATE_PLANNING_DEPT_ROLE]」を利用できます.
        - 営業部所属の社員は Role「:violet[SALES_DEPT_ROLE]」を利用できます.
        - R&D部所属の社員は Role「:gray[RESEARCH_AND_DEVELOPMENT_DEPT_ROLE]」を利用できます.
        '''
        )
    
    with st.expander('条件1：接続元IPの制限（開く）'):
        st.code('''
            CREATE NETWORK RULE allow_access_rule
            MODE = INGRESS
            TYPE = IPV4
            VALUE_LIST = ('203.0.113.100/25');
    
            CREATE NETWORK RULE block_access_rule
            MODE = INGRESS
            TYPE = IPV4
            VALUE_LIST = ('203.0.113.2/27', '203.0.113.63/27', '203.0.113.130/25' );
    
            CREATE NETWORK POLICY public_network_policy
            ALLOWED_NETWORK_RULE_LIST = ('allow_access_rule')
            BLOCKED_NETWORK_RULE_LIST=('block_access_rule');
            ''', language = "sql"
        )
        
    with st.expander('条件2：テーブルの構造とマスキング/アクセスポリシーの設定（開く）'):
        st.write('一般利用者の情報を収めたテーブル: SERVICE_SNOW.MASTER.CUSTOMERS')
        st.dataframe(_showed_table, hide_index=True, use_container_width=True)
        st.code('''
            CREATE MASKING POLICY AS age_mask as (val int) returns int ->
                CASE 
                    WHEN current_role() in ('SALES_DEPT_ROLE', 'CORPORATE_PLANNING_DEPT_ROLE', 'RESEARCH_AND_DEVELOPMENT_DEPT_ROLE') then val
                    ELSE null
                END;

            ALTER TABLE SERVICE_SNOW.MASTER.CUSTOMERS MODIFY COLUME '年代' SET MASKING POLICY age_mask;
            
            CREATE MASKING POLICY AS member_mask as (val boolean) returns boolean ->
                CASE 
                    WHEN current_role() in ('SECURITY_DEPT_ROLE', 'SALES_DEPT_ROLE', 'CORPORATE_PLANNING_DEPT_ROLE', 'RESEARCH_AND_DEVELOPMENT_DEPT_ROLE') then val
                    ELSE null
                END;

            ALTER TABLE SERVICE_SNOW.MASTER.CUSTOMERS MODIFY COLUME '本会員' SET MASKING POLICY member_mask;

            CREATE MASKING POLICY AS agreement_mask as (val boolean) returns boolean ->
                CASE 
                    WHEN current_role() in ('SECURITY_DEPT_ROLE', 'SALES_DEPT_ROLE', 'RESEARCH_AND_DEVELOPMENT_DEPT_ROLE') then val
                    ELSE null
                END;

            ALTER TABLE SERVICE_SNOW.MASTER.CUSTOMERS MODIFY COLUME 'データ利用の承諾可否' SET MASKING POLICY agreement_mask;


            CREATE MASKING POLICY AS email_mask as (val string) returns string ->
                CASE 
                    WHEN current_role() in ('SALES_DEPT_ROLE') then val
                    WHEN current_role() in ('CORPORATE_PLANNING_DEPT_ROLE') then regexp_replace(val,'.+\@','*****@') 
                    ELSE null 
                END;

            ALTER TABLE SERVICE_SNOW.MASTER.CUSTOMERS MODIFY COLUME 'メールアドレス' SET MASKING POLICY email_mask;


            CREATE ROW ACCESS POLICY non_agr_mask as (agr boolean) returns boolean ->
                CASE 
                    WHEN current_role() in ('SALES_DEPT_ROLE') then True
                    WHEN current_role() in ('RESEARCH_AND_DEVELOPMENT_DEPT_ROLE') and agr = True then True
                    ELSE False
                END;

            ALTER TABLE SERVICE_SNOW.MASTER.CUSTOMERS ADD ROW ACCESS POLICY non_member_mask ON ('データ利用の承諾可否');

            
            GRANT SELECT ON TABLE SERVICE_SNOW.MASTER.CUSTOMERS TO ROLE SECURITY_DEPT_ROLE;
            GRANT SELECT ON TABLE SERVICE_SNOW.MASTER.CUSTOMERS TO ROLE PURCHASING_DEPT_ROLE;
            GRANT SELECT ON TABLE SERVICE_SNOW.MASTER.CUSTOMERS TO ROLE CORPORATE_PLANNING_DEPT_ROLE;
            GRANT SELECT ON TABLE SERVICE_SNOW.MASTER.CUSTOMERS TO ROLE SALES_DEPT_ROLE;
            GRANT SELECT ON TABLE SERVICE_SNOW.MASTER.CUSTOMERS TO ROLE RESEARCH_AND_DEVELOPMENT_DEPT_ROLE;
            
            
            ''', language = "sql"
        )



def selecting_part( _items: list, _label: str ) -> object:                
    return st.selectbox(
        _label,
        _items,
        index=None
    )

def multiselecting_part( _items: list, _label: str ) -> object:
    _color_list = ['red','orange','green','blue','purple','gray']
    _style_setting =' '.join(['span[data-baseweb="tag"][aria-label="'+str(_role)+', close by backspace"]{background-color : '+str(_color_list[_i%len(_color_list)])+' ;}' for _i, _role in enumerate(_items)])
    st.markdown(f"""
        <style>
        {_style_setting}
        </style>
    """,unsafe_allow_html=True)

    return st.multiselect(
        _label,
        _items,
        []
    )

def showing_not_correct_ip_part( _selected_ip: str ) -> None: 
    re_ip = re.search(r'：(.+)\/',_selected_ip) if _selected_ip is not None else 'XXX.XXX.XXX.XXX'
    access_ip = re_ip.group(1) if re_ip is not None else 'XXX.XXX.XXX.XXX'
    st.code(
        f'''
        Failed to connect to DB: xxxxxxxxx.ap-northeast-1.aws.snowflakecomputing.com:443.
        IP {access_ip} is not allowed to access Snowflake.
        '''
    )
def showing_corrent_ip_part() -> None:
    st.code( "Connection successful!!" )
    time.sleep(.01)

def showing_sql_part( _role_name: str, _table_name: str ) -> None:
    use_role=re.search(r'：(.+)\）',_role_name).group(1) if _role_name is not None else 'PUBLIC'
    with st.status("選択されたRoleでSQLを実行"):
        time.sleep(.1)
    st.code(f'''
        USE ROLE {use_role};
        SELECT * FROM {_table_name};
        ''', language = "sql"
        )
def showing_not_granted_table_error_part( _table_name: str ) -> None:
    st.code(f'''
        {_table_name} does not exist or not authorized
        ''', language = "sql"
        )


def _masking_email(_table: pd, _colume_index: int) -> pd:
    _table.iloc[:,_colume_index] = _table.iloc[:,_colume_index].str.replace('.*@', '*****@', regex = True )
    return _table

def showing_table_part( _table_name:str ,_table: pd, _masking_type: str ) -> object:
    modified_table = _table.copy()
    
    ## 面倒くさくなったので分岐の種類は今回利用するケースのみ
    if _masking_type == 'AllMasking':
        ## 面倒いので初期化w
        modified_table = pd.DataFrame( None,index = _table.index.values.tolist(), columns = _table.columns.values )
    elif _masking_type == 'NotGranted':
        showing_not_granted_table_error_part( _table_name )
        modified_table=pd.DataFrame()
    elif _masking_type == 'Masking1':
        modified_table.iloc[:, 3] = None
        modified_table.iloc[:, 4] = None
    elif _masking_type == 'Masking2':
        modified_table.iloc[:, 3] = None
        _masking_email( modified_table, 4 )
    elif _masking_type == 'NotMasking':
        pass
    elif _masking_type == 'Masking3':
        modified_table.iloc[:, 4] = None
        modified_table = modified_table[modified_table["データ利用の承諾可否"] == True]
    else:
        showing_not_granted_table_error_part( _table_name )
        modified_table=pd.DataFrame()
    return modified_table


def registering_clear_user() -> None:
    ############
    ###### ここで正解したという情報を集計用にどこかに引き渡す処理を！　
    ############
    return 0
    
def checking_answer( _correct_answer: dict, _user_ans_ip: str, _user_ans_role: list ) -> bool:
    _re = True if _user_ans_ip == _correct_answer['IP'] and set( _user_ans_role ) == set( _correct_answer['ROLE'] ) else False
    return _re
    

def processing_correct_ans() -> None:
    st.success('正解')
    st.markdown('''
        :rainbow[★★★　おめでとぉぉぉぉぉおおおおう　★★★]
    ''')
    st.toast('Yeah!', icon='🎉')
    st.balloons()
    time.sleep(.5)
    st.toast('Yeah!', icon='🎉')
    st.balloons()
    time.sleep(.5)
    st.toast('Yeah!', icon='🎉')
    st.balloons()

    registering_clear_user()
    
def processing_incorrect_ans() -> None:
    st.error('ハズレ！')

def main():
    
    items_ip = [
        'インターネット',
        '社内ネットワークA（IPレンジ：203.0.113.0/26)', 
        '社内ネットワークB（IPレンジ：203.0.113.64/26）', ## CORRECT
        '社内ネットワークC（IPレンジ：203.0.113.128/26）', 
        '社内ネットワークD（IPレンジ：198.51.100.0/24）'
    ]

    items_role = [
        {'Dept': 'セキュリティ部（Role名：SECURITY_DEPT_ROLE）', 'MaskingType': 'Masking1' },
        {'Dept': '総務部（Role名：GENERAL_AFFAIRS_DEPT_ROLE）', 'MaskingType': 'NotGranted' },
        {'Dept': '購買部（Role名：PURCHASING_DEPT_ROLE）', 'MaskingType': 'AllMasking' },
        {'Dept': '経営企画部（Role名：CORPORATE_PLANNING_DEPT_ROLE）', 'MaskingType': 'Masking2' },
        {'Dept': '営業部（Role名：SALES_DEPT_ROLE）', 'MaskingType': 'NotMasking' },
        {'Dept': 'R&D部（Role名：RESEARCH_AND_DEVELOPMENT_DEPT_ROLE）', 'MaskingType': 'Masking3' }
    ]

    table_name = 'SERVICE_SNOW.MASTER.CUSTOMERS'
    table = pd.DataFrame(
        {
            'id': [1, 2, 3, 4, 5], 
            '年代': [10, 40, 20, 30, 50], 
            '本会員': [ True, False, True, True, False],
            'データ利用の承諾可否': [ True, False, False, True, False],
            'メールアドレス': [
                'tanaka.tarou@e-mail.com',
                'suzuki@mail-e.co.jp',
                'job_jirou@mail.com',
                'sasaki@company.co.jp',
                'snow@snow.com.jp'
            ]
        }
    )
    correct_answer = {
        'IP': items_ip[2],
        'ROLE': [ items_role[4]['Dept'],items_role[5]['Dept'] ]
    }
    
    header_animation()
    st.header( "問題", divider="rainbow")
    explaining_part(_showed_table=table)

    st.header( "回答", divider="blue")
    user_ans_ip = selecting_part( _items = items_ip, _label = 'Snowflakeにアクセスできるネットワークはどれでしょう？')
    user_ans_role = multiselecting_part( _items = [ l.get('Dept') for l in items_role], _label = '本会員数とデータ利用許諾の可否どちらも確認できる部門(Role)はどれでしょう？（複数選択）' )

    user_ans_results = checking_answer( _correct_answer = correct_answer, _user_ans_ip = user_ans_ip, _user_ans_role = user_ans_role ) if st.button("提出", type="primary") else None
    if user_ans_results is True: processing_correct_ans(); return 11
    if user_ans_results is False: processing_incorrect_ans(); return 10
     

    st.divider()
    st.header("検証",divider="green")
    st.info('実際に試して答えを導いてみましょう', icon="⭐️")

    selected_ip = selecting_part( _items = items_ip, _label = 'あなたはどこからSnowflakeに接続しますか？' )
    if selected_ip is None: st.write( "選択してください" ); return 0
    if selected_ip != correct_answer['IP']: showing_not_correct_ip_part( _selected_ip=selected_ip ); return 0
    if selected_ip == correct_answer['IP']: showing_corrent_ip_part()
        
    
    selected_role = selecting_part( _items=[ l.get('Dept') for l in items_role], _label = 'あなたはどの部署所属の人間に成り代わりますか？' )
    st.divider()

    if selected_role is None: return 0 
    showing_sql_part( _role_name = selected_role, _table_name = table_name )
    showed_table = showing_table_part( _table_name = table_name, _table = table, _masking_type = next((l["MaskingType"] for l in items_role if l["Dept"] == selected_role), None))
    
    st.dataframe(showed_table, hide_index=True, use_container_width=True)


from snowflake.snowpark import Session
from utils.utils import save_table, init_state
from utils.attempt_limiter import check_is_failed, init_attempt

def run(tab_name: str, session: Session):

    MAX_ATTEMPTS_MAIN = 3
    
    state = init_state(tab_name, session)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    result = main()
    if result not in (10,11) :
        return 0
    elif main_attempt.check_attempt():
        if result == 10:
            state["is_clear"] = True
            save_table(state, session)
            main_attempt.add_attempt()
    else:
        st.error("回答回数の上限に達しています。")


if __name__ == "__main__":
    main()


