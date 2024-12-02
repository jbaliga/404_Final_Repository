using System.Collections;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using UnityEngine;
using AustinHarris.JsonRpc;

public class angle : MonoBehaviour
{
    public Transform target; //the object we're getting the angle of
    class Rpc : JsonRpcService
    {
        angle a;
        public Rpc(angle a)
        {
            this.a = a;
        }

        [JsonRpcMethod]
        float getData()
        {
            return a.transform.position.y;
        }
    }
    Rpc rpc;
    // Start is called before the first frame update
    void Start()
    {
        rpc = new Rpc(this);
    }

    // Update is called once per frame
    void Update()
    {

        Vector3 targetDir = target.position-transform.position; //from
        targetDir.y = 0; //helps nullifies when looking up and down
        Vector3 forwardDir = transform.forward; //calcualtes the forward direction of the object
        forwardDir.y = 0; //helps nullifies when looking up and down
        float angle = Vector3.SignedAngle(targetDir, forwardDir, Vector3.up); //transform.forward is for Z-axis, transform.up is for y-axis, transform.right is for X-axis

        Debug.Log("Angle: " + angle);
    }
}
