# Secure Shell Service Over UDP
## Overview
The server listens on `UDP` port `5555` and supports basic shell operations such as connecting, executing commands, and disconnecting. 

It is able to process data up to `2048` bytes. Beyond that, an error message will be returned.

Due to the peculiarities of `UDP`, it is possible that packets are ignored by the server, or that the content of the packet is altered in transit.

The protocol involves sending and receiving packets (on top of `UDP`), each structured with a `header`, `size`, `content`, and `CRC32 checksum`.


## Packet Structure
Each packet consists of the following sections:

1. `Header` (`2` bytes)
    * Message ID: Determines the type of message being sent or received.
2. `Size` (`2` bytes)
    * Indicates the length of the content section.
3. `Content` (up to `2040` bytes)
    * Contains the actual data or command being transmitted.
4. `CRC32` (`4` bytes)
    * A checksum to verify packet integrity, calculated over the header, size, and content.


## Packet Details
* Header Format:
    * The message ID is a `4-digit` decimal number (ranging from `0000` to `9999`) that is converted to a `2-byte` hexadecimal format.
    * You'll have to use big endian when encoding the message ID
* Size Field:
    * This field indicates the length of the content section and is encoded in `2` bytes.
* Content:
    * The content is specific to the type of message. For a `CommandRequest` for example, it's the command to be executed.
* CRC32 Calculation:   
    * The checksum is computed over the header, size, and content using the `CRC32` algorithm.
    * The algorithm used is the same as the one present in Java (`java.util.zip.CRC32`).
    * The checksum is stored on `4` bytes allowing to detect a possible modification of the packet during the transit.
    * Same as the header, you'll have to use big endian when encoding your `CRC32` checksum

## Protocol Details
The protocol is structured as messages. Each message has its own identifier and content. The content of each message will be detailed later in this document.

Each message you send may be answered by an `ErrorMessage` containing an error code. You must check that each message received is not an error message before processing it.

To communicate with this server, it is necessary to follow the following steps in order (You'll receive an `ErrorMessage` if you fail):
1. Sending a `ConnectRequest` message with the string `CONNECT` as content.
2. Next you'll need to send a `CommandRequest` message with the content containing the command as a string (e.g: `ls`).
3. Finally disconnect by sending a `DisconnectRequest` message.

## Message Types
1. ConnectRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: `CONNECT`

    Server Response:
    * Header: `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: `[+] Connection established`
2. CommandRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: Command to be executed (e.g., `ls -l`)

    Server Response:
    * Header: `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: Output of the command execution (e.g., `[+]: file1 file2`)
3. DisconnectRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: `DISCONNECT` 

    Server Response:
    * Header:  `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: `[+] Disconnected`

## Error Handling 
If the server receives an unknown message ID, detects a checksum mismatch, or encounters any other error during processing, it responds with an `ErrorMessage`. 

The server can return an error under the following conditions:
* `Unknown Message ID`: If the header of the received packet does not match any valid message types.
* `Checksum Mismatch`: If the computed `CRC32` checksum does not match the checksum provided in the packet.
* `Invalid Content`: If the content of a command or request is improperly formatted or not recognized.
* `Client State Errors`: If a command is received when the client is not in the `CONNECTED` state (for example, trying to send a command before connecting).

The server's error response will include:
* Header: `\x17\x73` (`6003` in hexadecimal -> `ErrorMessage`)
* Content: A descriptive error message (e.g., `[-] Unknown message ID`, `[-] Checksum mismatch`, or `[-] Invalid command format`, etc...).

## String encoding
Strings are encoded in `UTF-8`.
