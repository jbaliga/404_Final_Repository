using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class angleAndDistance : MonoBehaviour
{
    public Transform target;  // The object we're getting the angle of
    public Transform t1;      // First transform for distance calculation
    public Transform t2;      // Second transform for distance calculation

    private TcpListener server;
    private bool serverRunning = false;  // Track server state
    private Thread serverThread;
    private TcpClient client;
    private NetworkStream stream;

    void Start()
    {
        // Start server in a new thread to avoid freezing Unity's main thread
        serverThread = new Thread(StartServer);
        serverThread.IsBackground = true;
        serverThread.Start();
    }

    void StartServer()
    {
        try
        {
            server = new TcpListener(IPAddress.Any, 12345);
            server.Start();
            serverRunning = true;  // Mark server as running
            Debug.Log("Server started on port 12345, waiting for client...");

            client = server.AcceptTcpClient();  // Accept client connection
            Debug.Log("Client connected!");
            stream = client.GetStream();
        }
        catch (Exception ex)
        {
            Debug.LogError("Failed to start server: " + ex.Message);
        }
    }

    void Update()
    {
        if (client != null && client.Connected && stream != null)
        {
            // Calculate angle between the player and the target
            float angleValue = CalculateAngle();

            // Calculate distance between t1 and t2
            float distanceValue = CalculateDistance();

            Debug.Log("Angle: " + angleValue);
            Debug.Log("Distance: " + distanceValue);

            // Send both angle and distance to the client
            SendAngleAndDistanceData(angleValue, distanceValue);
        }
    }

    float CalculateAngle()
    {
        Vector3 targetDir = target.position - transform.position;  // Direction to target
        targetDir.y = 0;  // Nullify vertical direction
        Vector3 forwardDir = transform.forward;  // Forward direction of the player
        forwardDir.y = 0;  // Nullify vertical direction
        return Vector3.SignedAngle(targetDir, forwardDir, Vector3.up);  // Calculate signed angle
    }

    float CalculateDistance()
    {
        return Vector3.Distance(t1.position, t2.position);  // Calculate distance between t1 and t2
    }

    void SendAngleAndDistanceData(float angle, float distance)
    {
        if (stream != null && client.Connected)
        {
            // Send angle and distance as a comma-separated string
            string data = $"{angle},{distance}";
            byte[] dataBytes = Encoding.UTF8.GetBytes(data);
            stream.Write(dataBytes, 0, dataBytes.Length);
            stream.Flush();
        }
    }

    void OnApplicationQuit()
    {
        if (serverRunning)
        {
            serverRunning = false;  // Mark server as stopped

            // Safely close client and server
            if (client != null)
            {
                client.Close();
            }
            if (server != null)
            {
                server.Stop();
            }
            if (serverThread != null && serverThread.IsAlive)
            {
                serverThread.Abort();
            }
        }
    }
}

