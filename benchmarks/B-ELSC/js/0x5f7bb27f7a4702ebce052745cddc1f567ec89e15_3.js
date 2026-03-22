var contract = artifacts.require("EthGame");

module.exports = function(deployer, network, accounts) {
  deployer.deploy(
    contract,
    accounts[0],
    accounts[1],
    accounts[2],
    accounts[3],
    accounts[4],
    "10000000000000000000"
  );
};
