resource "aws_security_group" "ec2_sg" {
name_prefix = "ec2-sg-"

ingress {
from_port   = 22
to_port     = 22
protocol    = "tcp"
cidr_blocks = ["0.0.0.0/0"]
}

egress {
from_port   = 0
to_port     = 0
protocol    = "-1"
cidr_blocks = ["0.0.0.0/0"]
}

tags = {
Name = "${var.instance_name}-sg"
}
}

resource "aws_instance" "this" {
count = var.instance_count

ami                    = var.ami_id
instance_type          = var.instance_type
key_name               = var.key_name
vpc_security_group_ids = [aws_security_group.ec2_sg.id]

root_block_device {
volume_size = 8
volume_type = "gp3"
}

tags = {
Name = "${var.instance_name}-${count.index + 1}"
}
}
