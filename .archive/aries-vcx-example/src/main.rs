use aries_vcx_agent::{Agent, InitConfig, PoolInitConfig, WalletInitConfig};
use url::Url;

#[tokio::main]
async fn main() {
    // use local file path for genesis file
    let gen_path =
        "/home/arminveres/Projects/bachelor-thesis-23/impl/von-network/genesis/iiw_demo_genesis";
    let pool_name = "localhost";

    let pool_init = PoolInitConfig {
        genesis_path: gen_path.to_string(),
        pool_name: pool_name.to_string(),
    };

    let wallet_init = WalletInitConfig {
        wallet_name: "armins-wallet".to_string(),
        wallet_key: "6BC3E23D262CAB2D992A5CDC0405FE38D1763402BC45B00BF0C426AC12D1B49C".to_string(),
        wallet_kdf: "ARGON2I_INT".to_string(),
    };

    let endpoint = Url::parse("http://localhost:9000").expect("Should be a legitimate url");

    let init_config = InitConfig {
        agency_config: None,
        enterprise_seed: "my_seed_000000000000000000000000".to_string(),
        pool_config: pool_init,
        wallet_config: wallet_init,
        service_endpoint: endpoint,
    };

    let agent = Agent::initialize(init_config)
        .await
        .expect("Initialization must work!");
}
