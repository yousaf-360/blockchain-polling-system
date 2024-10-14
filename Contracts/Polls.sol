// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PollingSystem {
    
    // Poll structure to store poll details
    struct Poll {
        
        string question;
        string[] options;
        mapping(address => bool) hasVoted;  // Tracks who has voted
        mapping(uint256 => uint256) voteCount;  // Tracks votes per option
        uint256 totalVotes;  // Total number of votes for the poll
    }

    // Array to store all polls
    Poll[] public polls;

    // Contract owner
    address public owner;

    // Events for poll creation and voting
    event PollCreated(uint256 pollId, string question);
    event Voted(address indexed voter, uint256 pollId, uint256 optionId);

    // Constructor to set contract owner
    constructor() {
        owner = msg.sender;
    }



    // Modifier to ensure that the voter has not already voted
    modifier hasNotVoted(uint256 pollId) {
        require(!polls[pollId].hasVoted[msg.sender], "You have already voted.");
        _;
    }

   // Add this variable to your contract
uint256 public pollsCount;  // Total number of polls created

// Update the createPoll function
function createPoll(string memory _question, string[] memory _options) public {
    Poll storage newPoll = polls.push();  // Add new poll to the polls array
    newPoll.question = _question;  // Set poll question
    newPoll.totalVotes = 0;  // Initialize total votes
    newPoll.options = _options;  // Set options directly

    // Emit PollCreated event with pollId and question
    emit PollCreated(polls.length - 1, _question);

    pollsCount++;  // Increment the total polls count
}

    // Function to vote on a poll (checks if the voter has not voted already)
    function vote(uint256 _pollId, uint256 _optionId) public hasNotVoted(_pollId) {
        Poll storage poll = polls[_pollId];  // Retrieve the poll by pollId
        require(_optionId < poll.options.length, "Invalid option");

        poll.hasVoted[msg.sender] = true;  // Mark the sender as voted
        poll.voteCount[_optionId]++;  // Increment the vote count for the selected option
        poll.totalVotes++;  // Increment total votes for the poll

        // Emit Voted event with voter address, pollId, and optionId
        emit Voted(msg.sender, _pollId, _optionId);
    }

    // Function to get results of a poll
    function getResults(uint256 _pollId) public view returns (uint256[] memory) {
        Poll storage poll = polls[_pollId];  // Retrieve the poll by pollId
        uint256[] memory results = new uint256[](poll.options.length);  // Array to store results
        
        // Loop through each option and store the vote count
        for (uint256 i = 0; i < poll.options.length; i++) {
            results[i] = poll.voteCount[i];
        }

        return results;
    }

    // Function to get the details of a specific poll
    function getPoll(uint256 _pollId) public view returns (string memory, string[] memory, uint256[] memory) {
        Poll storage poll = polls[_pollId];  // Retrieve the poll by pollId
        uint256[] memory voteCounts = new uint256[](poll.options.length);  // Array to store vote counts
        
        // Store vote counts for each option
        for (uint256 i = 0; i < poll.options.length; i++) {
            voteCounts[i] = poll.voteCount[i];
        }

        return (poll.question, poll.options, voteCounts);  // Return question, options, and vote counts
    }

    // Function to get the list of all poll questions
    function getAllPolls() public view returns (string[] memory) {
        string[] memory questions = new string[](polls.length);  // Array to store poll questions
        
        // Loop through all polls and store their questions
        for (uint256 i = 0; i < polls.length; i++) {
            questions[i] = polls[i].question;
        }

        return questions;
    }

    // Function to check if a specific user has voted in a poll
    function hasUserVoted(uint256 _pollId, address _voter) public view returns (bool) {
        return polls[_pollId].hasVoted[_voter];
    }
}
