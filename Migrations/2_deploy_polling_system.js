const PollingSystem = artifacts.require("PollingSystem");

module.exports = function (deployer) {
  deployer.deploy(PollingSystem);
};

