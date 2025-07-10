from faq_crawling import q_a_list
import pandas as pd

q_a_df = pd.DataFrame(q_a_list)

q_a_df[1] = q_a_df[1].apply(lambda x: ' '.join(x))

q_a_df.columns = ['Q', 'A']

# csv로 저장
q_a_df.to_csv("faq.csv", index=True, encoding="utf-8")