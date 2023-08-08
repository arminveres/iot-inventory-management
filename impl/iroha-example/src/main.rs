use iroha_client::client::Client;
use iroha_core::prelude::*;
use iroha_data_model::{
    account::AccountId,
    isi::{InstructionBox, MintBox},
    metadata::UnlimitedMetadata,
    prelude::*,
    transaction::Executable::Instructions,
};

use serde_json;
use std::{fs::File, str::FromStr};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Either read in config from json file
    let config_loc = "./config.json";
    let file = File::open(config_loc).expect("Config file is loading normally.");
    let config = serde_json::from_reader(file).unwrap();

    // Create an Iroha client
    let client = Client::new(&config)?;

    /*
    // or give it manually
    let kp = KeyPair::new(
        PublicKey::from_str(
            r#"ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"#,
        )?,
        PrivateKey::from_hex(
            Algorithm::Ed25519,
            "9ac47abf59b356e0bd7dcbbbb4dec080e302156a48ca907e47cb6aea1d32719e7233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"
                .into(),
        )?
    )?;

    let (pub_key, priv_key) = kp.clone().into();
    let account_id: AccountId = "alice@wonderland".parse()?;
    let config = ConfigurationProxy {
        public_key: Some(pub_key),
        private_key: Some(priv_key),
        account_id: Some(account_id),
        torii_api_url: Some(SmallStr::from_string(
            iroha_config::torii::uri::DEFAULT_API_URL.to_owned(),
        )),
        ..ConfigurationProxy::default()
    };

    let client = Client::new(&config)?;
    */

    // ============================================================================================
    // Registering a Domain
    // ============================================================================================

    // Create a domain Id
    let looking_glass: DomainId = "looking_glass".parse()?;
    // Create an ISI (Iroha Instruction)
    let create_looking_glass = RegisterBox::new(Domain::new(looking_glass));
    // client.submit(create_looking_glass);
    client.submit_with_metadata(create_looking_glass, UnlimitedMetadata::default())?;

    // prepare a transaction by building it
    // let metadata = UnlimitedMetadata::default();
    // let instructions = vec![create_looking_glass.into()];
    // let tx = client
    //     .build_transaction(Instructions(instructions), metadata)
    //     .unwrap();

    // client.submit_transaction(&tx).unwrap();

    // ============================================================================================
    // Registering an Account
    // ============================================================================================

    let longhand_account_id = AccountId {
        name: "white_rabbit".parse()?,
        domain_id: "looking_glass".parse()?,
    };
    let account_id = "white_rabbit@looking_glass"
        .parse::<AccountId>()
        .expect("Valid, no whitespaces and single @ char");

    assert_eq!(account_id, longhand_account_id);

    let pubkey = get_key_from_white_rabbit().unwrap();

    let account = Account::new(account_id.clone(), vec![pubkey]);
    // let idbox = IdentifiableBox::from(account);
    // let create_account = RegisterBox::new(idbox);
    let create_account = RegisterBox::new(account);

    let instructions: Vec<InstructionBox> = vec![create_account.into()];
    let tx = client
        .build_transaction(Instructions(instructions), UnlimitedMetadata::default())
        .unwrap();
    client.submit_transaction(&tx).expect("Account created");

    // or just do it directly
    // client.submit(create_account)?;

    // ============================================================================================
    // Registering and mintint assets
    // ============================================================================================
    // Create an asset
    let asset_def_id = AssetDefinitionId::from_str("time#looking_glass")
        .expect("Valid, because the string contains no whitespace, has a single '#' character and is not empty after");

    // Initialise the registration time
    let register_time =
        RegisterBox::new(AssetDefinition::fixed(asset_def_id.clone()).mintable_once());

    // Submit a registration time
    client.submit(register_time)?;

    // Create a MintBox using a previous asset and account
    let mint = MintBox::new(
        12.34_f64.try_to_value()?,
        IdBox::AssetId(AssetId::new(asset_def_id, account_id)),
    );

    // Submit a minting transaction
    client.submit_all([<MintBox as Into<InstructionBox>>::into(mint)])?;

    Ok(())
}

fn get_key_from_white_rabbit() -> Result<PublicKey, Box<dyn std::error::Error>> {
    // TODO: (aver) save private part
    let keypair = KeyPair::generate()?;
    Ok(keypair.public_key().to_owned())
}
