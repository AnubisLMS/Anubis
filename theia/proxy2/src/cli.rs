use clap::{command, value_parser, ArgMatches, Arg, ArgAction};


pub fn new() -> ArgMatches {
    command!()
    .color(clap::ColorChoice::Always)
    .author("John McCann Cunniff Jr <johncunniff1248@gmail.com>")
    .about("")
    .version("2.0.0")

    // Proxy settings
    .arg(Arg::new("host").long("host").default_value("0.0.0.0"))
    .arg(Arg::new("port").long("port").default_value("5000").value_parser(value_parser!(u16)))
    .arg(Arg::new("max_connections").long("max_connections").default_value("64").value_parser(value_parser!(u32)))

    // DB settings
    .arg(Arg::new("db_user").long("db_user").env("DB_USER").default_value("anubis"))
    .arg(Arg::new("db_password").long("db_password").env("DB_PASSWORD").default_value("anubis"))
    .arg(Arg::new("db_database").long("db_database").env("DB_DATABASE").default_value("anubis"))
    .arg(Arg::new("db_host").long("db_host").env("DB_HOST").default_value("127.0.0.1"))
    .arg(Arg::new("db_port").long("db_port").env("DB_PORT").default_value("3306").value_parser(value_parser!(u16)))

    // JWT settings
    .arg(Arg::new("secret_key").long("secret_key").env("SECRET_KEY").default_value("DEBUG"))

    // Debug
    .arg(Arg::new("debug").short('d').long("debug").env("DEBUG").action(ArgAction::SetTrue).help("enable debugging"))
    .get_matches()
}