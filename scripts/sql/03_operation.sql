-- データベース・スキーマ・ロール選択
use role sysadmin;
use database swtt_test;
use schema public;

-- ウェアハウスのスケーリング変更クエリ
USE ROLE ACCOUNTADMIN;
ALTER WAREHOUSE COMPUTE_WH SET
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 10  // ここを変更！
;
use role sysadmin; // SYSADMINに戻しておく。

-- 各テーブルが空であることを確認する
use role sysadmin; 
select * from swtt_test.public.submit2;

use role sysadmin;
select * from swtt_test.public.hand_data;

-- 各テーブルがもし空でなかったら、このクエリを実行する。※ACCOUNTADMIN で実行しないように注意すること！！！
use role sysadmin;
/* // 本番中に誤って実行しないようにコメントアウト。
create or replace TABLE SWTT_TEST.PUBLIC.SUBMIT2 (
	TEAM_ID VARCHAR(16777216),
	PROBLEM_ID VARCHAR(16777216),
	TIMESTAMP TIMESTAMP_NTZ(9),
	IS_CLEAR BOOLEAN,
	KEY VARCHAR(16777216),
	MAX_ATTEMPTS NUMBER(38,0)
);
*/

use role sysadmin;
/* // 本番中に誤って実行しないようにコメントアウト。
create or replace TABLE SWTT_TEST.PUBLIC.HAND_DATA (
	ID NUMBER(38,0) autoincrement start 1 increment 1 noorder,
	TEAM_ID VARCHAR(16777216),
	HAND VARCHAR(1)
);
*/


-- 特定の問題の回答状況（FALSE）リセットクエリ
-- なお、リセット後、再ログインするまでは状態が更新されないため注意！
select * from submit2;
DELETE FROM SUBMIT2 
WHERE TRUE
    AND is_clear=false
    //AND problem_id='be_positive' // ここに問題IDを入れる
    //AND team_id='' // ここにチームIDを入れる
    // 問題ID：be_positive, whats_squad, chat_with_ai, real_ice, rsp, nw_role, sort_services, real_wanage
;

-- 特定の問題の回答状況水増しクエリ
select * from submit2;
INSERT INTO SWTT_TEST.PUBLIC.SUBMIT2 (TEAM_ID, PROBLEM_ID, TIMESTAMP, IS_CLEAR, KEY, MAX_ATTEMPTS)
SELECT SUBSTR(UUID_STRING(), 1, 10), 'be_positive', CURRENT_TIMESTAMP, TRUE, NULL, NULL;
// 上の問題IDだけ変更する：be_positive, whats_squad, chat_with_ai, real_ice, rsp, nw_role, sort_services, real_wanage



-- ランキング取得クエリ
USE ROLE SYSADMIN;
WITH solved_problems AS (
    -- 各チームごとの最初に解けた問題（is_clear=true）のタイムスタンプを取得
    SELECT
        team_id,
        problem_id,
        MIN(timestamp) AS first_clear_time
    FROM submit2
    WHERE is_clear = true
    GROUP BY team_id, problem_id
),
team_scores AS (
    -- 各チームごとに、解けた問題の数と、解答速度の合計を計算
    SELECT
        team_id,
        COUNT(problem_id) AS solved_problems_count,  -- 解けた問題数
        SUM(DATEDIFF(SECOND, TO_TIMESTAMP('2024-09-01 00:00:00'), first_clear_time)) AS total_solve_time  -- 解答までの時間（秒単位）
    FROM solved_problems
    GROUP BY team_id
)
-- 最終的なスコアの計算。例えば、解けた問題数を重視し、速度も加味するスコアリングを行う
SELECT
    team_id,
    solved_problems_count,
    -- スコアの計算例（解けた問題数を重視しつつ、解答速度も加味）
    solved_problems_count * 100000 - (total_solve_time / 3600) AS score  -- 解答速度を1時間単位で考慮
FROM team_scores
ORDER BY score DESC;
