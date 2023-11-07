PbeePATH='/path/to/pbee/folder'

# ---
sed -i "5s,=.*,= '${PbeePATH}',g" ./modules/configure.py
