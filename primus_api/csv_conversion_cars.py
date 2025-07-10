from api_call_car import registered_evs # 전기차 정보 담은 리스트
import pandas as pd

## 전기차 정보 데이터프레임으로 변환 후 csv로 저장

df_evs = pd.DataFrame(registered_evs)


# 파일 이름과 "저장 경로"를 지정합니다.
output_csv_file = 'registered_evs_data.csv'

# index=False: DataFrame의 기본 인덱스(0, 1, 2...)를 CSV 파일에 저장 x
# encoding='utf-8-sig': 한글 깨짐 방지를 위해 'utf-8-sig' 인코딩을 사용
df_evs.to_csv(output_csv_file, index=False, encoding='utf-8-sig')

print(f"'{output_csv_file}' 파일로 성공적으로 저장되었습니다.")

# 저장된 파일의 일부를 다시 불러와서 확인 (선택 사항)
# loaded_df = pd.read_csv(output_csv_file, encoding='utf-8-sig')
# print("\n저장된 CSV 파일을 다시 불러와 확인:")
# print(loaded_df.head())