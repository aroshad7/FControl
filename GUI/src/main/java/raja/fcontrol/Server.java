/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package raja.fcontrol;

import java.io.*;
import java.net.*;

/**
 *
 * @author aroshaD
 */
public class Server implements Runnable {

    private String incoming_data;
    private boolean updated = false;

    public synchronized String getData() {
        return incoming_data;
    }

    private synchronized void setData(String _data) {
        incoming_data = _data;
    }

    public synchronized boolean isUpdated() {
        return updated;
    }

    public synchronized void setUpdatedStatus(boolean flag) {
        updated = flag;
    }

    private ServerSocket mysocket;
    private Socket connectionSocket;

    @Override
    public void run() {
        System.out.println("Creating Server");
        try {
            mysocket = new ServerSocket(5555);       //Create server on port 5555
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        while (true) {
            try {
                System.out.println("Server waiting for connection");
                connectionSocket = mysocket.accept();            //Create connection socket to accept client,freez untill client connects

                BufferedReader reader = new BufferedReader(new InputStreamReader(connectionSocket.getInputStream()));   //readers & writers for client 
                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(connectionSocket.getOutputStream()));

                System.out.println("Server connected to client");
                writer.write("*Connect OK*\r\n");
                writer.flush();

                while (true) //infinite loop to read client
                {
                    String data = (reader.readLine().trim());
                    setData(data);
                    setUpdatedStatus(true);
                    System.out.println(data);
                    writer.write("*Data ACK*\r\n");
                    writer.flush();
                    if (data.contains("exit")) {
                        break;
                    }

                }
                connectionSocket.close();
            } catch (Exception ex) {  //This exception is thrown every time the connection is cloased by the client
                System.out.println("Closing Connection...");
                //ex.printStackTrace();
            }
            if (this.getData().contains("exit")) {
                System.out.println("Closing Server...");                
                break;
            }
        }
    }

}
