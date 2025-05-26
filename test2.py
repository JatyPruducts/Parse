import pandas as pd
import test1 as check

#https://автолига.рф/search.html?article=313971XF0C&brand=NISSAN&withAnalogs=1

#чтение данных из excel
df = pd.read_excel('articles.xlsx')

df["Best_FLag"] = False


for index, row in df.iterrows():
    brand = row['Производитель']
    article = row['Артикул']
    print("ok")
    if check.get_top(brand, article) == "BEST":
        df.at[index, "Best_FLag"] = True

df.to_excel("articles_update.xlsx", index=False)
