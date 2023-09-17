use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let alice_url = "http://0.0.0.0:8031";
    let bob_url = "http://0.0.0.0:8041";
    let ledger_url = "http://0.0.0.0:9000";

    let client = reqwest::Client::new();

    // register a did!
    let resp = client
        .post(ledger_url.to_owned() + "/register")
        .body("{\"seed\": \"Alice000000000000000000000000001\", \"role\": \"TRUST_ANCHOR\", \"alias\": \"Alice\"}")
        .send()
        .await?
        // .text()
        .json::<HashMap<String, String>>()
        .await?;
    println!("{:#?}", resp);

    let resp = client
        .post(ledger_url.to_owned() + "/register")
        .body("{\"seed\": \"Bob00000000000000000000000000001\", \"role\": \"TRUST_ANCHOR\", \"alias\": \"Bob\"}")
        .send()
        .await?
        // .text()
        .json::<HashMap<String, String>>()
        .await?;
    println!("{:#?}", resp);

    // let resp = reqwest::get(url.to_owned() + "/wallet/did")
    //     .await?
    //     .text()
    //     // .json::<HashMap<String, String>>()
    //     .await?;
    // println!("{:#?}", resp);

    // let resp = reqwest::get(alice_url.to_owned() + "/connections")
    //     .await?
    //     .text()
    //     // .json::<HashMap<String, String>>()
    //     .await?;
    // println!("{:#?}", resp);

    // create invitation for bob
    let resp = client
        .post(alice_url.to_owned()+"/out-of-band/create-invitation")
        .body("{\"handshake_protocols\": [ \"did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0\" ], \"use_public_did\": false }")
        .send()
        .await?
        .text()
        .await?;
    // println!("{:#?}", resp);
    println!("{resp}");

    Ok(())
}
