PbeePATH=''

# ---
sed -i "5s,=.*,= '${PbeePATH}',g" ./modules/configure.py
