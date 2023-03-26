use std::rc::Rc;

use sqlx::Connection;
use sqlx::mysql::MySqlPoolOptions;
use sqlx::mysql::MySqlPool;
use sqlx::mysql::MySql;
use sqlx::pool::PoolConnection;
use futures::executor::block_on;

#[derive(Debug)]
#[derive(sqlx::FromRow)]
pub struct User {
    id: String,
    name: String,
}


#[derive(Clone, Debug)]
pub struct AnubisDB {
    pool: MySqlPool
}

impl AnubisDB {
    pub fn new() -> AnubisDB {
        AnubisDB {
            pool: block_on(MySqlPoolOptions::new()
                .max_connections(5)
                .connect("mysql://anubis:anubis@127.0.0.1/anubis"))
                .expect("unable to connect to db")
        }
    }

    fn get_connection(self) -> PoolConnection<MySql> {
        let fut = self.pool.acquire();
        block_on(fut).expect("Could not acquire connection")
    }

    pub fn get_users(self) -> Vec<User> {
        let mut conn = self.get_connection();
        let stream = sqlx::query_as::<_, User>("SELECT * FROM user;").fetch_all(&mut conn);
        block_on(stream).expect("Could not fetch users")
    }
}

