var contract = artifacts.require("HOT");

module.exports = function(deployer) {
  deployer.deploy(contract, 1000000, "HOT", 10);
};
