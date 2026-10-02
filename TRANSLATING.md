# 번역 지침

`ko-game.json`(게임 문자열 키 → 한국어)을 고칠 때 지키는 규칙입니다. 게임 화면과 [grun.run](https://www.grun.run)이 같은 말을 쓰게 하는 것이 목표입니다.

## 원칙

- **영어 원문만 보고 직접 번역합니다.** 다른 한글패치·번역본의 문장을 옮겨 오지 않습니다.
- 영웅·아이템·유물·능력 이름은 `ko-game.json`에 이미 있는 이름을 그대로 씁니다. 같은 이름은 어디서나 같게 씁니다.
- 영웅 이름: 이리니, 호영, 레이나, 유나, 주리, 아리아, 닉스, 폴렌, 니클라스, 피오나, 로완, 스코른, 로건, 풍케, 틸리, 구스타프, 라트나, 립, 카르수, 밍, 피멘타, 살, 드라고미르, 카이, 그레이스.

## 형식 (하나라도 어기면 게임에서 깨진다)

- `{0}`, `{amount}`, `{floorNode.FloorNumber + 1}` 같은 중괄호는 글자 하나 바꾸지 않는다. 어순만 옮길 수 있다.
- `{0:choose(Feminine|Masculine|Neutral):A|B|C}` 는 앞부분을 그대로 두고 `A|B|C`만 번역한다. 한국어는 보통 셋이 같다.
- `[텍스트]<태그>` 는 대괄호 안만 번역하고 `<태그>`는 그대로. `<b>`, `</b>`, `<color=…>`, `<sprite …>`, `<br>`도 그대로 둔다.
- 줄바꿈(`\n`) 수와 위치는 원문과 같게.
- 원문 앞뒤 공백은 신경 쓰지 않아도 된다.

## 문체

| 종류 | 문체 | 예 |
|---|---|---|
| 효과·설명·안내·튜토리얼·대화상자·이벤트 본문·선택지·결과 | 합니다체 | 샤드 50개를 얻습니다. |
| UI 라벨·버튼·제목·칭호·통계 이름 | 짧은 명사형, 마침표 없음 | 상점 새로고침, 받은 피해 |
| 설정(Lore) 소개 글 | 해라체 서술 | 로완은 6년 동안 균열에서 수정을 캐냈다. |
| 만화(Comics) | 내레이션은 해라체, 대사는 말투 그대로 | |

- 'you'는 대부분 생략한다. 'your guild/your Heroes'는 '길드', '아군'·'영웅'.
- 기계 번역 티(…하는 것이 가능합니다, 그것은, 당신의)를 피하고 짧게.
- 수치 표기는 사이트를 따른다: `[샤드 {0}]<shard>`, `[{0}의 냉기]<frost>`, `{0}초`, `{0}%`.

## 용어 (사이트 기준, 게임 전용 추가분 포함)

| 영어 | 한국어 | 영어 | 한국어 |
|---|---|---|---|
| Hero / enemy | 영웅 / 적 | Ability (일반) | 능력 |
| Active Ability | 액티브 스킬 | Passive Ability | 패시브 능력 |
| cast | 시전 | auto attack | 기본 공격 |
| Stat(s) / Basic Stats / Primary Stat | 능력치 / 기본 능력치 / 주 능력치 | damage | 피해 |
| Damage Amp | 피해 증폭 | Attack Range | 사거리 |
| Starting Mana / Max Mana | 시작 마나 / 최대 마나 | HP/S | 초당 체력 회복 |
| Shield(s) / Lasting | 보호막 / 영구 | Crit / Crit Damage | 치명타 / 치명타 피해 |
| Stun / Taunt / Stealth | 기절 / 도발 / 은신 | heal | 치유 |
| Burn / Poison / Frost | 화상 / 중독 / 냉기 | Omnivamp | 모든 피해 흡혈 |
| Rush / Stall | 러시 / 지연 | Backup / Backup Only | 지원 / 지원 전용 |
| Reserves / battlefield | 대기석 / 전장 | Shards / Generate | 샤드 / 생성 |
| Reroll | 새로고침 | Rank / Rank up | 랭크 / 랭크업 |
| Specialization (B랭크) | 전문화 | Class Upgrade | 클래스 업그레이드 |
| Common / Unique / Rare / Epic / Legendary | 일반 / 고유 / 희귀 / 에픽 / 전설 | relic / item / shop | 유물 / 아이템 / 상점 |
| run / act / Act Boss / Elite | 런 / 액트 / 액트 보스 / 엘리트 | Fight #N / combat | N번째 전투 / 전투 |
| Quest / Reward | 퀘스트 / 보상 | Starter Kit | 스타터 키트 |
| Rift / Rift Storm | 균열 / 균열 폭풍 | Red Rift | 붉은 균열 |
| Rift Seal, Rift Anchor | 균열 봉인석 | Rift Sealing Protocol | 균열 봉인 작전 |
| Rift Contract | 균열 계약 | Rift Key / Key Fragment | 균열 열쇠 / 열쇠 조각 |
| Boss Token | 보스 토큰 | Emergency Rewind | 긴급 되감기 |
| Endless Mode / Cycle / Floor | 무한 모드 / 회차 / 층 | Leaderboard / Win Streak | 순위표 / 연승 |
| Trial | 시련 | Campfire | 모닥불 |
| Train / Retrain | 훈련 / 재훈련 | Mastery | 숙련 |
| Compendium | 도감 | Difficulty | 난이도 |
| Awakened / Awakening | 각성자 / 각성 | Breaker(s) | 브레이커 |
| guild / Department of Guild Affairs | 길드 / 길드 관리국 | Aegis Global (회사) | 이지스 글로벌 |

클래스: 전사, 탱커, 선봉, 암살자, 결투가, 신비술사, 마법사.
