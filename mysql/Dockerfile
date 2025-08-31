FROM mysql:latest

# init.sql 파일 복사
COPY init.sql /docker-entrypoint-initdb.d/

# 한글 설정
RUN echo "[client]" > /etc/mysql/conf.d/my.cnf && \
    echo "default-character-set=utf8mb4" >> /etc/mysql/conf.d/my.cnf && \
    echo "" >> /etc/mysql/conf.d/my.cnf && \
    echo "[mysql]" >> /etc/mysql/conf.d/my.cnf && \
    echo "default-character-set=utf8mb4" >> /etc/mysql/conf.d/my.cnf && \
    echo "" >> /etc/mysql/conf.d/my.cnf && \
    echo "[mysqldump]" >> /etc/mysql/conf.d/my.cnf && \
    echo "default-character-set = utf8mb4" >> /etc/mysql/conf.d/my.cnf && \
    echo "" >> /etc/mysql/conf.d/my.cnf && \
    echo "[mysqld]" >> /etc/mysql/conf.d/my.cnf && \
    echo "init_connect = \"SET collation_connection = utf8_general_ci\"" >> /etc/mysql/conf.d/my.cnf && \
    echo "init-connect = 'SET NAMES utf8'" >> /etc/mysql/conf.d/my.cnf && \
    echo "character-set-server = utf8mb4" >> /etc/mysql/conf.d/my.cnf && \
    echo "collation-server = utf8mb4_unicode_ci" >> /etc/mysql/conf.d/my.cnf && \
    chmod 644 /etc/mysql/conf.d/my.cnf