docker exec -it db bash;
psql -U postgres -d app;

INSERT INTO users(username, email,password,role) VALUES

('user','user@gmail.com','$2y$10$Sh8z.OQi0GJ9D3coCTg5vOVrjCfa/fkj4tDtmYEBeNVhOsgJhfYMG','USER'),

('admin','admin@gmail.com','$2y$10$Sh8z.OQi0GJ9D3coCTg5vOVrjCfa/fkj4tDtmYEBeNVhOsgJhfYMG','ADMIN');