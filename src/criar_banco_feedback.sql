CREATE DATABASE feedback_database;
use feedback_database;
CREATE TABLE feedback (
    id int auto_increment primary key,
    avaliacao int,
    mensagem text,
    data_envio timestamp default current_timestamp
);

select * from feedback;